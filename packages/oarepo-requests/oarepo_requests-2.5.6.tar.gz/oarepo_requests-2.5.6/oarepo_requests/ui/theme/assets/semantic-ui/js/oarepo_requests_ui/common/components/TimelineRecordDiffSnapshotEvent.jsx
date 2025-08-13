import React from "react";
import PropTypes from "prop-types";
import { Icon, Message } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { ErrorBoundary } from "react-error-boundary";
import _isArray from "lodash/isArray";
import {
  getRequestStatusIcon,
  getFeedMessage,
  GenericActionEvent,
  DiffOperationAccordionTable,
} from "@js/oarepo_requests_common";

const DiffFallbackMessage = ({ error }) => (
  <Message negative>
    <Message.Header>
      {i18next.t("Unable to parse diff data")}
    </Message.Header>
    <p>{i18next.t("There was an error processing the diff data.")}</p>
    {error?.message && <pre>{error.message}</pre>}
  </Message>
);

DiffFallbackMessage.propTypes = {
  error: PropTypes.object.isRequired,
};

export const TimelineRecordDiffSnapshotEvent = ({ event }) => {
  const eventIcon = getRequestStatusIcon("edited");
  const feedMessage = getFeedMessage("edited");

  // Parse and process diff data
  const renderDiffTables = () => {
    if (!event.payload?.diff) return null;

    const diffOperations = JSON.parse(event.payload.diff);

    if (!_isArray(diffOperations)) {
      return null;
    }

    // Handle case where there are no changes
    if (diffOperations.length === 0) {
      return (
        <div>
          <Icon name="info circle" />
          {i18next.t("No changes detected between versions")}
        </div>
      );
    }

    // Group operations by type
    const operationsByType = diffOperations.reduce((groups, op) => {
      const operationType = op.op.toLowerCase();
      if (!groups[operationType]) {
        groups[operationType] = [];
      }
      groups[operationType].push(op);
      return groups;
    }, {});

    return (
      <ErrorBoundary FallbackComponent={DiffFallbackMessage}>
        <div className="diff-tables-container ml-5">
          <DiffOperationAccordionTable
            operations={operationsByType.add || []}
            operationType="add"
          />
          <DiffOperationAccordionTable
            operations={operationsByType.remove || []}
            operationType="remove"
          />
          <DiffOperationAccordionTable
            operations={operationsByType.replace || []}
            operationType="replace"
          />
        </div>
      </ErrorBoundary>
    );
  };

  return (
    <GenericActionEvent
      event={event}
      eventIcon={eventIcon}
      feedMessage={feedMessage}
      ExtraContent={renderDiffTables()}
    />
  );
};

TimelineRecordDiffSnapshotEvent.propTypes = {
  event: PropTypes.object.isRequired,
};
