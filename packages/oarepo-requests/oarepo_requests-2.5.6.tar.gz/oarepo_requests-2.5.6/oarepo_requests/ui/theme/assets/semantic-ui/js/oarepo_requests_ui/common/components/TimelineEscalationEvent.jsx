import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { GenericActionEvent } from "./GenericActionEvent";

// placeholder component for escalation as data is not yet available
// to whom the request is escalated etc.
export const TimelineEscalationEvent = ({ event }) => {
  return (
    <GenericActionEvent
      event={event}
      eventIcon={{ name: "arrow circle up" }}
      feedMessage={i18next.t("escalated")}
    />
  );
};

TimelineEscalationEvent.propTypes = {
  event: PropTypes.object,
};
