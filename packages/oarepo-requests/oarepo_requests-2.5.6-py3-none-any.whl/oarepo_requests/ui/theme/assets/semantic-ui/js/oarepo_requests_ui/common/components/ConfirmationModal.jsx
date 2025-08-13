import React, { useState } from "react";
import { Confirm, Message, Icon } from "semantic-ui-react";
import {
  WarningMessage,
  ConfirmationModalConfirmButton,
  ConfirmationModalCancelButton,
  RequestCommentInput,
  REQUEST_TYPE,
  MAX_COMMENT_LENGTH,
} from "@js/oarepo_requests_common";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import PropTypes from "prop-types";

export const ConfirmationModal = ({
  requestActionName,
  requestOrRequestType,
  requestExtraData,
  isOpen,
  close,
  onConfirmAction,
}) => {
  let caseSpecificProps = {};
  const [comment, setComment] = useState("");
  const handleChange = (event, value) => {
    setComment(value);
  };

  const [length, setLength] = useState(comment.length);

  const handleLengthChange = (length) => setLength(length);

  const dangerous = requestExtraData?.dangerous;
  const baseConfirmDialogProps = {
    content: dangerous ? <WarningMessage /> : i18next.t("Are you sure?"),
    onConfirm: () => {
      onConfirmAction(comment);
      close();
    },
    onCancel: () => {
      close();
      setComment("");
    },
    cancelButton: <ConfirmationModalCancelButton />,
    open: isOpen,
  };
  switch (requestActionName) {
    case REQUEST_TYPE.CREATE:
      caseSpecificProps = createConfirmDialogProps(requestOrRequestType);
      break;
    case REQUEST_TYPE.SUBMIT:
      caseSpecificProps = submitConfirmDialogProps(requestOrRequestType);
      break;
    case REQUEST_TYPE.CANCEL:
      caseSpecificProps = cancelConfirmDialogProps(requestOrRequestType);
      break;
    case REQUEST_TYPE.ACCEPT:
      caseSpecificProps = acceptConfirmDialogProps(
        requestOrRequestType,
        dangerous
      );
      break;
    case REQUEST_TYPE.DECLINE:
      caseSpecificProps = declineConfirmDialogProps(
        requestOrRequestType,
        comment,
        handleChange,
        length,
        handleLengthChange
      );
      break;
    default:
      break;
  }
  const modalProps = { ...baseConfirmDialogProps, ...caseSpecificProps };
  return (
    <Confirm
      className="requests dangerous-action-confirmation-modal"
      {...modalProps}
    />
  );
};

ConfirmationModal.propTypes = {
  requestActionName: PropTypes.string,
  requestOrRequestType: PropTypes.object,
  requestExtraData: PropTypes.object,
  isOpen: PropTypes.bool,
  close: PropTypes.func,
  onConfirmAction: PropTypes.func,
};

const createConfirmDialogProps = (requestOrRequestType) => ({
  header: `${i18next.t("Create request")} (${requestOrRequestType?.name})`,
  confirmButton: (
    <ConfirmationModalConfirmButton negative content={i18next.t("Proceed")} />
  ),
  content: (
    <WarningMessage
      message={i18next.t(
        "Are you sure you wish to proceed? After this request is accepted, it will not be possible to reverse the action."
      )}
    />
  ),
});

const submitConfirmDialogProps = (requestOrRequestType) => ({
  header: `${i18next.t("Submit request")} (${requestOrRequestType.name})`,
  confirmButton: (
    <ConfirmationModalConfirmButton negative content={i18next.t("Proceed")} />
  ),
  content: (
    <WarningMessage
      message={i18next.t(
        "Are you sure you wish to proceed? After this request is accepted, it will not be possible to reverse the action."
      )}
    />
  ),
});

const cancelConfirmDialogProps = (requestOrRequestType) => ({
  header: `${i18next.t("Cancel request")} (${requestOrRequestType.name})`,
  confirmButton: (
    <ConfirmationModalConfirmButton
      content={i18next.t("Cancel request")}
      negative
    />
  ),
});

const acceptConfirmDialogProps = (requestOrRequestType, dangerous) => ({
  header: `${i18next.t("Accept request")} (${requestOrRequestType.name})`,
  confirmButton: (
    <ConfirmationModalConfirmButton
      positive={!dangerous}
      negative={dangerous}
      content={i18next.t("Accept")}
    />
  ),
  content: dangerous && (
    <WarningMessage
      message={i18next.t(
        "This action is irreversible. Are you sure you wish to accept this request?"
      )}
    />
  ),
});

const declineConfirmDialogProps = (
  requestOrRequestType,
  comment,
  handleChange,
  length,
  handleLengthChange
) => {
  return {
    header: `${i18next.t("Decline request")} (${requestOrRequestType.name})`,
    confirmButton: (
      <ConfirmationModalConfirmButton
        content={i18next.t("Decline")}
        negative
        disabled={length > MAX_COMMENT_LENGTH}
      />
    ),
    content: (
      <div className="content">
        <RequestCommentInput
          comment={comment}
          handleChange={handleChange}
          length={length}
          setLength={handleLengthChange}
          maxCommentLength={MAX_COMMENT_LENGTH}
        />
        <Message>
          <Icon name="info circle" className="text size large" />
          <span>
            {i18next.t(
              "It is highly recommended to provide an explanation for the rejection of the request. Note that it is always possible to provide explanation later on the request timeline."
            )}
          </span>
        </Message>
      </div>
    ),
  };
};
