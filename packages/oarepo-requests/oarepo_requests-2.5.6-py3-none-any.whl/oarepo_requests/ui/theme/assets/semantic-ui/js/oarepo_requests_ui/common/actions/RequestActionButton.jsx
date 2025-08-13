import React from "react";
import { Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import {
  useModalControlContext,
  useAction,
  ConfirmationModal,
} from "@js/oarepo_requests_common";
import { useConfirmationModal } from "@js/oarepo_ui";

export const RequestActionButton = ({
  requestOrRequestType,
  extraData,
  isMutating,
  iconName,
  action,
  buttonLabel,
  requireConfirmation,
  requestActionName,
  ...uiProps
}) => {
  const formik = useFormikContext();

  const { isOpen, close, open } = useConfirmationModal();

  const modalControl = useModalControlContext();
  const { isLoading, mutate: requestAction } = useAction({
    action,
    requestOrRequestType,
    formik,
    modalControl,
    requestActionName,
  });

  const handleClick = () => {
    if (requireConfirmation) {
      open();
    } else {
      requestAction();
    }
  };

  return (
    <>
      <Button
        title={buttonLabel}
        onClick={handleClick}
        className="requests request-action-button"
        icon
        labelPosition="left"
        loading={isLoading}
        disabled={isMutating > 0}
        {...uiProps}
      >
        <Icon name={iconName} />
        {buttonLabel}
      </Button>
      <ConfirmationModal
        requestActionName={requestActionName}
        requestOrRequestType={requestOrRequestType}
        requestExtraData={extraData}
        onConfirmAction={(comment) => {
          requestAction(comment);
        }}
        isOpen={isOpen}
        close={close}
      />
    </>
  );
};

RequestActionButton.propTypes = {
  requestOrRequestType: PropTypes.object,
  extraData: PropTypes.object,
  isMutating: PropTypes.number,
  iconName: PropTypes.string,
  action: PropTypes.func,
  buttonLabel: PropTypes.string,
  requireConfirmation: PropTypes.bool,
  requestActionName: PropTypes.string,
};

export default RequestActionButton;
