import React from "react";
import {
  getRequestStatusIcon,
  getFeedMessage,
} from "@js/oarepo_requests_common";
import PropTypes from "prop-types";
import { GenericActionEvent } from "./GenericActionEvent";

export const TimelineActionEvent = ({ event }) => {
  const eventIcon = getRequestStatusIcon(event.payload.event);
  const feedMessage = getFeedMessage(event.payload.event);

  return (
    <GenericActionEvent
      event={event}
      feedMessage={feedMessage}
      eventIcon={eventIcon}
    />
  );
};

TimelineActionEvent.propTypes = {
  event: PropTypes.object,
};
