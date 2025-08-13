import React from "react";
import { useConfirmationModal } from "@js/oarepo_ui";
import { Dimmer, Loader, Modal, Button } from "semantic-ui-react";
import { useFormik, FormikProvider } from "formik";
import _isEmpty from "lodash/isEmpty";
import {
  ModalControlContextProvider,
  RequestModalContentAndActions,
} from "@js/oarepo_requests_common";
import PropTypes from "prop-types";
import { useIsMutating } from "@tanstack/react-query";
import { useCallbackContext } from "../contexts";

/**
 * @typedef {import("../../record-requests/types").Request} Request
 * @typedef {import("../../record-requests/types").RequestType} RequestType
 * @typedef {import("react").ReactElement} ReactElement
 */

/** @param {{ request: Request?, requestType: RequestType?, header: string | ReactElement, trigger: ReactElement, ContentComponent: ReactElement, requestCreationModal: Boolean }} props */

export const RequestModal = ({
  request,
  requestType,
  header,
  trigger,
  ContentComponent,
  requestCreationModal,
}) => {
  const { isOpen, close: closeModal, open: openModal } = useConfirmationModal();
  const { setActionsLocked } = useCallbackContext();

  const formik = useFormik({
    initialValues: !_isEmpty(request?.payload)
      ? { payload: request.payload }
      : { payload: {} },
  });
  const { resetForm, setErrors } = formik;

  const isMutating = useIsMutating();

  const onClose = () => {
    setErrors({});
    resetForm();
    closeModal();
    setActionsLocked(false);
  };
  return (
    <FormikProvider value={formik}>
      <ModalControlContextProvider
        value={{
          isOpen,
          closeModal: onClose,
          openModal,
        }}
      >
        <Modal
          className="requests-request-modal form-modal"
          as={Dimmer.Dimmable}
          blurring
          onClose={onClose}
          onOpen={openModal}
          open={isOpen}
          trigger={trigger || <Button content="Open Modal" />}
          closeIcon
          closeOnDocumentClick={false}
          closeOnDimmerClick={false}
          aria-labelledby="request-modal-header"
          aria-describedby="request-modal-desc"
        >
          <Dimmer active={isMutating > 0}>
            <Loader inverted size="large" />
          </Dimmer>
          <Modal.Header as="h1" id="request-modal-header">
            {header}
          </Modal.Header>
          <RequestModalContentAndActions
            request={request}
            requestType={requestType}
            ContentComponent={ContentComponent}
            requestCreationModal={requestCreationModal}
            isMutating={isMutating}
            onClose={onClose}
          />
        </Modal>
      </ModalControlContextProvider>
    </FormikProvider>
  );
};

RequestModal.propTypes = {
  request: PropTypes.object,
  requestType: PropTypes.object,
  header: PropTypes.oneOfType([PropTypes.string, PropTypes.element]),
  trigger: PropTypes.element,
  ContentComponent: PropTypes.func,
  requestCreationModal: PropTypes.bool,
};
