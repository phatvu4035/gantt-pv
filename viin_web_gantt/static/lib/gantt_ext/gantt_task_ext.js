function TaskFactory() {

  /**
   * Build a new Task
   */
  this.build = function (id, name, code, level, start, duration, collapsed, zoom) {
    // Set at beginning of day
    var adjusted_start = computeStart(start, zoom);
    var calculated_end = computeEndByDuration(adjusted_start, duration, zoom);
    return new Task(id, name, code, level, adjusted_start, calculated_end, duration, collapsed);
  };

}

/*
 * Overwrite to check to exclude task has only one children, and children has start = parent start
 * to avoid circular
 */
Task.prototype.moveTo = function (start, ignoreMilestones, propagateToInferiors) {
  if (start instanceof Date) {
    start = start.getTime();
  }

  var originalPeriod = {
    start: this.start,
    end:   this.end
  };

  var wantedStartMillis = start;

  //set a legal start
  start = computeStart(start, this.master.gantt.zoom);

  //if depends, start is set to max end + lag of superior
  start = this.computeStartBySuperiors(start);

  var end = computeEndByDuration(start, this.duration, this.master.gantt.zoom);


  //check milestones compatibility
  if (!this.checkMilestonesConstraints(start,end,ignoreMilestones))
      return false;

  if (this.start != start || this.start != wantedStartMillis) {
    //in case of end is milestone it never changes!
    //if (!ignoreMilestones && this.endIsMilestone && end != this.end) {
    //  this.master.setErrorOnTransaction("\"" + this.name + "\"\n" + GanttMaster.messages["END_IS_MILESTONE"], this);
    //  return false;
    //}
    this.start = start;
    this.end = end;
    //profiler.stop();

    //check global boundaries
    if (this.start < this.master.minEditableDate || this.end > this.master.maxEditableDate) {
      this.master.setErrorOnTransaction("\"" + this.name + "\"\n" +GanttMaster.messages["CHANGE_OUT_OF_SCOPE"], this);
      return false;
    }


    // bicch 22/4/2016: quando si sposta un task con child a cavallo di holidays, i figli devono essere shiftati in workingDays, non in millisecondi, altrimenti si cambiano le durate
    // when moving children you MUST consider WORKING days,
    var panDeltaInWM = getDistanceInUnits(new Date(originalPeriod.start),new Date(this.start), this.master.gantt.zoom);

    //loops children to shift them
    var children = this.getChildren();
    // Check to exclude task has only one children
    var shouldUpdateChildren = true;
    if ( children.length == 1) {
        var chTask = children[0];
        if(chTask.start == this.start) {
          shouldUpdateChildren = false;
        }
    }
    if(shouldUpdateChildren) {
      for (var i = 0; i < children.length; i++) {
          var ch = children[i];
          var chStart=incrementDateByUnits(new Date(ch.start),panDeltaInWM, this.master.gantt.zoom);
          ch.moveTo(chStart,false,false);
      }
    }
    
    // debugger
    if (!updateTree(this)) {
      return false;
    }

    if (propagateToInferiors) {
      this.propagateToInferiors(end);
      var todoOk = true;
      var descendants = this.getDescendant();
      for (var i = 0; i < descendants.length; i++) {
        ch = descendants[i];
        if (!ch.propagateToInferiors(ch.end))
          return false;
      }
    }
  }

  return true;
};

//<%---------- SET PERIOD ---------------------- --%>
Task.prototype.setPeriod = function(start, end) {

    if (start instanceof Date) {
        start = start.getTime();
    }

    if (end instanceof Date) {
        end = end.getTime();
    }

    var originalPeriod = {
        start: this.start,
        end: this.end,
        duration: this.duration
    };
    var zoom = this.master.getStoredZoomLevelMaster(this.master.tasks);
    //compute legal start/end //todo mossa qui R&S 30/3/2016 perchè altrimenti il calcolo della durata, che è stato modificato sommando giorni, sbaglia
    start = computeStart(start, zoom);
    end = computeEnd(end, zoom);
    var newDuration = recomputeDuration(start, end, zoom);
    // debugger
    //if are equals do nothing and return true
    if (start == originalPeriod.start && end == originalPeriod.end && newDuration == originalPeriod.duration) {
        return true;
    }
    if (newDuration == this.duration) { // is shift
        return this.moveTo(start, false, true);
    }
    var wantedStartMillis = start;

    var children = this.getChildren();

    if (this.master.shrinkParent && children.length > 0) {
        var chPeriod = this.getChildrenBoudaries();
        start = chPeriod.start;
        end = chPeriod.end;
    }

    //cannot start after end
    if (start > end) {
        start = end;
    }

    //if there are dependencies compute the start date and eventually moveTo
    var startBySuperiors = this.computeStartBySuperiors(start);
    if (startBySuperiors != start) {
        return this.moveTo(startBySuperiors, false, true);
    }
    var somethingChanged = false;

    if (this.start != start || this.start != wantedStartMillis) {
        this.start = start;
        somethingChanged = true;
    }

    //set end
    var wantedEndMillis = end;

    if (this.end != end || this.end != wantedEndMillis) {
        this.end = end;
        somethingChanged = true;
    }
    this.duration = recomputeDuration(this.start, this.end, zoom);
    //profilerSetPer.stop();
    //nothing changed exit
    if (!somethingChanged)
        return true;

    //cannot write exit
    if (!this.canWrite) {
        this.master.setErrorOnTransaction("\"" + this.name + "\"\n" + GanttMaster.messages["CANNOT_WRITE"], this);
        return false;
    }

    //external dependencies: exit with error
    if (this.hasExternalDep) {
        this.master.setErrorOnTransaction("\"" + this.name + "\"\n" + GanttMaster.messages["TASK_HAS_EXTERNAL_DEPS"], this);
        return false;
    }

    var todoOk = true;

    //I'm restricting
    var deltaPeriod = originalPeriod.duration - this.duration;
    var restricting = deltaPeriod > 0;
    var enlarging = deltaPeriod < 0;
    var restrictingStart = restricting && (originalPeriod.start < this.start);
    var restrictingEnd = restricting && (originalPeriod.end > this.end);
    if (restricting) {
        //loops children to get boundaries
        var bs = Infinity;
        var be = 0;
        for (var i = 0; i < children.length; i++) {

            var ch = children[i];
            if (restrictingEnd) {
                be = Math.max(be, ch.end);
            } else {
                bs = Math.min(bs, ch.start);
            }
        }

        if (restrictingEnd) {
            this.end = Math.max(be, this.end);
        } else {
            this.start = Math.min(bs, this.start);
        }
        // if current zoom is by hours then coumpute it in differenc way
        this.duration = recomputeDuration(this.start, this.end, this.master.gantt.zoom);

        if (this.master.shrinkParent) {
            todoOk = updateTree(this);
        }

    } else {

        //check global boundaries
        if (this.start < this.master.minEditableDate || this.end > this.master.maxEditableDate) {
            this.master.setErrorOnTransaction("\"" + this.name + "\"\n" + GanttMaster.messages["CHANGE_OUT_OF_SCOPE"], this);
            todoOk = false;
        }

        //console.debug("set period: somethingChanged",this);
        if (todoOk) {
            todoOk = updateTree(this);
        }
    }
    // debugger
    if (todoOk) {
        todoOk = this.propagateToInferiors(end);
    }
    return todoOk;
};

Task.prototype.computeStartBySuperiors = function (proposedStart) {
  var zoom = this.master.getStoredZoomLevelMaster(this.master.tasks);
  return computeStart(proposedStart, zoom);
};

//<%---------- PROPAGATE TO INFERIORS ---------------------- --%>
Task.prototype.propagateToInferiors = function (end) {
  return true;
};
