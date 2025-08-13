import { i18next } from "@translations/oarepo_dashboard";
import React from "react";

export const getUserIcon = (receiver) => {
  return receiver?.is_ghost ? "user secret" : "users";
};

export const getReceiver = (request) => {
  if (request?.receiver?.reference?.auto_approve) return null;
  if (!Array.isArray(request.receiver)) {
    return request.receiver?.links?.self_html ? (
      <a
        href={request.receiver.links.self_html}
        target="_blank"
        rel="noopener noreferrer"
      >
        {i18next.t("Recipient: {{receiver}}.", {
          receiver: request.receiver.label,
          interpolation: { escapeValue: false },
        })}
      </a>
    ) : (
      i18next.t("Recipient: {{receiver}}.", {
        receiver: request.receiver.label,
        interpolation: { escapeValue: false },
      })
    );
  } else {
    return (
      <span>
        {i18next.t("Recipient:")}{" "}
        {request.receiver.map((receiver, index) => {
          const label =
            index === request.receiver.length - 1
              ? receiver.label
              : `${receiver.label}, `;
          return receiver?.links?.self_html ? (
            <a
              href={receiver.links.self_html}
              target="_blank"
              rel="noopener noreferrer"
              key={label}
            >
              {label}
            </a>
          ) : (
            <span key={label}>{label}</span>
          );
        })}
      </span>
    );
  }
};
