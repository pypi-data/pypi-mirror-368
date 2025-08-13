import React from "react";
import { Button } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";

export const ConfirmationModalConfirmButton = (uiProps) => (
  <Button
    className="requests confirmation-modal-confirm-button"
    content={i18next.t("OK")}
    {...uiProps}
  />
);
