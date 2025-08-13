import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Placeholder, Message } from "semantic-ui-react";
import _isEmpty from "lodash/isEmpty";
import { useRequestContext } from "@js/oarepo_requests_common";
import PropTypes from "prop-types";
import { useIsMutating } from "@tanstack/react-query";
import { CreateRequestButton } from "./CreateRequestButton";

/**
 * @param {{  applicableRequestsLoading: boolean, applicableRequestsLoadingError: Error }} props
 */
export const CreateRequestButtonGroup = ({
  applicableRequestsLoading,
  applicableRequestsLoadingError,
}) => {
  const { requestTypes, requestButtonsIconsConfig } = useRequestContext();
  const createRequests = requestTypes?.filter(
    (requestType) => requestType.links.actions?.create
  );
  const isMutating = useIsMutating();

  let content;

  if (applicableRequestsLoading) {
    content = (
      <Placeholder>
        {Array.from({ length: 2 }).map((_, index) => (
          <Placeholder.Paragraph key={index}>
            <Placeholder.Line length="full" />
            <Placeholder.Line length="medium" />
          </Placeholder.Paragraph>
        ))}
      </Placeholder>
    );
  } else if (applicableRequestsLoadingError) {
    content = (
      <Message negative className="rel-mb-1">
        <Message.Header>
          {i18next.t("Error loading request types")}
        </Message.Header>
      </Message>
    );
  } else if (_isEmpty(createRequests)) {
    return null; // No need to render anything if there are no requests
  } else {
    content = createRequests.map((requestType) => {
      const header =
        requestType.stateful_name || requestType.name || requestType.type_id;
      const buttonIconProps =
        requestButtonsIconsConfig[requestType.type_id] ||
        requestButtonsIconsConfig?.default;

      return (
        <CreateRequestButton
          key={requestType.type_id}
          requestType={requestType}
          isMutating={isMutating}
          buttonIconProps={buttonIconProps}
          header={header}
        />
      );
    });
  }

  return (
    <div className="requests-create-request-buttons borderless">{content}</div>
  );
};

CreateRequestButtonGroup.propTypes = {
  applicableRequestsLoading: PropTypes.bool,
  applicableRequestsLoadingError: PropTypes.object,
};
