import React from "react";
import PropTypes from "prop-types";
import { Form, Divider } from "semantic-ui-react";
import { CustomFields } from "react-invenio-forms";
import sanitizeHtml from "sanitize-html";

/**
 * @typedef {import("../../record-requests/types").RequestType} RequestType
 * @typedef {import("formik").FormikConfig} FormikConfig
 */

/** @param {{ requestType: RequestType, customSubmitHandler: (e) => void }} props */
export const CreateRequestModalContent = ({
  requestType,
  customFields,
  allowedHtmlAttrs,
  allowedHtmlTags,
}) => {
  const description =
    requestType?.stateful_description || requestType?.description;

  const sanitizedDescription = sanitizeHtml(description, {
    allowedTags: allowedHtmlTags,
    allowedAttributes: allowedHtmlAttrs,
  });

  return (
    <>
      {description && (
        <p
          id="request-modal-desc"
          dangerouslySetInnerHTML={{ __html: sanitizedDescription }}
        ></p>
      )}
      {customFields?.ui && (
        <Form id="request-form">
          <CustomFields
            config={customFields?.ui}
            templateLoaders={[
              (widget) => import(`@templates/custom_fields/${widget}.js`),
              (widget) => import(`react-invenio-forms`),
            ]}
            fieldPathPrefix="payload"
          />
          <Divider hidden />
        </Form>
      )}
    </>
  );
};

CreateRequestModalContent.propTypes = {
  requestType: PropTypes.object.isRequired,
  customFields: PropTypes.object,
  allowedHtmlAttrs: PropTypes.object,
  allowedHtmlTags: PropTypes.array,
};
