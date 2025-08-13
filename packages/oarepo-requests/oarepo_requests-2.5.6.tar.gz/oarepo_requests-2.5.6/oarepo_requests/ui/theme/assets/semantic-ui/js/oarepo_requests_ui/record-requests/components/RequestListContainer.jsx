import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Placeholder, Message } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import { RequestList } from ".";
import { useRequestContext } from "@js/oarepo_requests_common";
import PropTypes from "prop-types";

/**
 * @param {{ requestsLoading: boolean, requestsLoadingError: Error }} props
 */
export const RequestListContainer = ({
  requestsLoading,
  requestsLoadingError,
}) => {
  const { requests } = useRequestContext();
  let openRequests = requests?.filter(
    (request) =>
      request.is_open || request?.status_code.toLowerCase() === "created"
  );

  if (!requestsLoading && !requestsLoadingError && _isEmpty(openRequests)) {
    return null;
  }

  return (
    <div className="requests-my-requests borderless">
      {requestsLoading && (
        <Placeholder fluid>
          {Array.from({ length: 2 }).map((_, index) => (
            <Placeholder.Paragraph key={index}>
              <Placeholder.Line length="full" />
              <Placeholder.Line length="medium" />
            </Placeholder.Paragraph>
          ))}
        </Placeholder>
      )}

      {requestsLoadingError && (
        <Message negative>
          <Message.Header>{i18next.t("Error loading requests")}</Message.Header>
        </Message>
      )}

      {!requestsLoading && !requestsLoadingError && (
        <RequestList requests={openRequests} />
      )}
    </div>
  );
};

RequestListContainer.propTypes = {
  requestsLoading: PropTypes.bool.isRequired,
  requestsLoadingError: PropTypes.object,
};
