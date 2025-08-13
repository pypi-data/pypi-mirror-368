import React, { useEffect } from "react";
import { Button, Message } from "semantic-ui-react";
import PropTypes from "prop-types";
import {
  useAction,
  useRequestContext,
  saveAndSubmit,
  ConfirmationModal,
  REQUEST_TYPE,
} from "@js/oarepo_requests_common";
import { useConfirmationModal } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { useCallbackContext } from "../contexts";

// Directly create and submit request without modal
const DirectCreateAndSubmit = ({
  requestType,
  requireConfirmation,
  isMutating,
}) => {
  const { isOpen, close, open } = useConfirmationModal();
  const { actionsLocked, setActionsLocked } = useCallbackContext();

  const {
    isLoading,
    mutate: createAndSubmit,
    isError,
    error,
    reset,
  } = useAction({
    action: saveAndSubmit,
    requestOrRequestType: requestType,
  });
  const { requestButtonsIconsConfig } = useRequestContext();
  const buttonIconProps =
    requestButtonsIconsConfig[requestType.type_id] ||
    requestButtonsIconsConfig?.default;
  const buttonContent =
    requestType?.stateful_name || requestType?.name || requestType?.type_id;

  const handleClick = () => {
    setActionsLocked(true);
    if (requireConfirmation) {
      open();
    } else {
      createAndSubmit();
    }
  };
  useEffect(() => {
    let timeoutId;
    if (isError) {
      timeoutId = setTimeout(() => {
        reset();
      }, 2500);
      setActionsLocked(false);
    }
    return () => {
      clearTimeout(timeoutId);
    };
  }, [isError, reset]);

  return (
    <React.Fragment>
      <Button
        // applicable requests don't have a status
        className={`requests request-create-button ${requestType?.type_id}`}
        fluid
        title={buttonContent}
        content={buttonContent}
        loading={isLoading}
        disabled={actionsLocked || isMutating > 0}
        onClick={() => handleClick()}
        labelPosition="left"
        {...buttonIconProps}
      />
      {isError && (
        <Message negative className="rel-mb-1">
          <Message.Header>
            {(error?.response?.data?.errors?.length > 0 &&
              error.directSubmitMessage) ||
              i18next.t("Request could not be executed.")}
          </Message.Header>
        </Message>
      )}
      <ConfirmationModal
        requestActionName={REQUEST_TYPE.SUBMIT}
        requestOrRequestType={requestType}
        requestExtraData={requestType}
        onConfirmAction={() => {
          createAndSubmit();
        }}
        isOpen={isOpen}
        close={close}
      />
    </React.Fragment>
  );
};

DirectCreateAndSubmit.propTypes = {
  requestType: PropTypes.object,
  requireConfirmation: PropTypes.bool,
  isMutating: PropTypes.number,
};

export default DirectCreateAndSubmit;
