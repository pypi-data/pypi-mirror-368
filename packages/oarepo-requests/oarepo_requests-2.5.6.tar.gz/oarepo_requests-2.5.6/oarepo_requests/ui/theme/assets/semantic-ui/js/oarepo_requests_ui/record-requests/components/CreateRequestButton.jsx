import React from "react";
import { Button } from "semantic-ui-react";
import { RequestModal, CreateRequestModalContent } from ".";
import { DirectCreateAndSubmit } from "@js/oarepo_requests_common";
import PropTypes from "prop-types";
import { useCallbackContext } from "../../common";

export const CreateRequestButton = ({
  requestType,
  isMutating,
  buttonIconProps,
  header,
}) => {
  const { actionsLocked, setActionsLocked } = useCallbackContext();
  const { dangerous, has_form: hasForm } = requestType;
  const needsDialog = dangerous || hasForm;

  if (!hasForm) {
    return (
      <DirectCreateAndSubmit
        requestType={requestType}
        requireConfirmation={dangerous}
        isMutating={isMutating}
      />
    );
  }

  if (needsDialog) {
    return (
      <RequestModal
        requestType={requestType}
        header={header}
        requestCreationModal
        trigger={
          <Button
            className={`requests request-create-button ${requestType.type_id}`}
            fluid
            title={header}
            content={header}
            onClick={() => setActionsLocked(true)}
            disabled={actionsLocked || isMutating > 0}
            labelPosition="left"
            {...buttonIconProps}
          />
        }
        ContentComponent={CreateRequestModalContent}
      />
    );
  }

  return null;
};

CreateRequestButton.propTypes = {
  requestType: PropTypes.object,
  isMutating: PropTypes.number.isRequired,
  buttonIconProps: PropTypes.object,
  header: PropTypes.string.isRequired,
};
