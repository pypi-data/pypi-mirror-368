import React from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import {
  Dimmer,
  Loader,
  Modal,
  Button,
  Icon,
  Message,
} from "semantic-ui-react";
import { useFormikContext } from "formik";
import { mapLinksToActions } from "@js/oarepo_requests_common";
import PropTypes from "prop-types";
import { useQuery, useIsMutating } from "@tanstack/react-query";
import { httpApplicationJson } from "@js/oarepo_ui";

export const RequestModalContentAndActions = ({
  request,
  requestType,
  onSubmit,
  ContentComponent,
  requestCreationModal,
  onClose,
}) => {
  const { errors } = useFormikContext();
  const error = errors?.api;

  const {
    data,
    error: customFieldsLoadingError,
    isLoading,
  } = useQuery(
    ["applicableCustomFields", requestType?.type_id || request?.type],
    () =>
      httpApplicationJson.get(
        `/requests/configs/${requestType?.type_id || request?.type}`
      ),
    {
      enabled: !!(requestType?.type_id || request?.type),
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    }
  );
  const customFields = data?.data?.custom_fields;
  const allowedHtmlAttrs = data?.data?.allowedHtmlAttrs;
  const allowedHtmlTags = data?.data?.allowedHtmlTags;

  const requestTypeProperties = data?.data?.request_type_properties;
  const isMutating = useIsMutating();
  const modalActions = mapLinksToActions(
    requestCreationModal ? requestType : request,
    customFields,
    requestTypeProperties
  );

  return (
    <React.Fragment>
      <Dimmer active={isLoading}>
        <Loader inverted />
      </Dimmer>
      <Modal.Content>
        {error && (
          <Message negative>
            <Message.Header>{error}</Message.Header>
          </Message>
        )}
        {customFieldsLoadingError && (
          <Message negative>
            <Message.Header>
              {i18next.t("Form fields could not be fetched.")}
            </Message.Header>
          </Message>
        )}
        <ContentComponent
          request={request}
          requestType={requestType}
          onCompletedAction={onSubmit}
          customFields={customFields}
          modalActions={modalActions}
          allowedHtmlAttrs={allowedHtmlAttrs}
          allowedHtmlTags={allowedHtmlTags}
        />
      </Modal.Content>
      <Modal.Actions>
        {modalActions.map(({ name, component: ActionComponent }) => (
          <ActionComponent
            key={name}
            request={request}
            requestType={requestType}
            extraData={requestTypeProperties}
            isMutating={isMutating}
          />
        ))}
        <Button onClick={onClose} icon labelPosition="left">
          <Icon name="cancel" />
          {i18next.t("Close")}
        </Button>
      </Modal.Actions>
    </React.Fragment>
  );
};

RequestModalContentAndActions.propTypes = {
  request: PropTypes.object,
  requestType: PropTypes.object,
  ContentComponent: PropTypes.func,
  requestCreationModal: PropTypes.bool,
  onSubmit: PropTypes.func,
  onClose: PropTypes.func,
};
