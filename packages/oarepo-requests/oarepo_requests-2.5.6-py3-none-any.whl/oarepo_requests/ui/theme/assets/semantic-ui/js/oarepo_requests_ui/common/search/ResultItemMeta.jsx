import React from "react";
import { Icon, Item } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_dashboard";
import { getReceiver, getUserIcon } from "./util";
import { DateTime } from "luxon";
import PropTypes from "prop-types";

// eliminate code duplication
export const ResultItemMeta = ({ result }) => {
  let creatorName = result.created_by.label;

  return (
    <Item.Meta>
      <small>
        {i18next.t("Opened by {{creatorName}} on {{created}}.", {
          creatorName: creatorName,
          created: result.created,
          interpolation: { escapeValue: false },
        })}{" "}
        {result.receiver && getReceiver(result)}
      </small>
      <small className="right floated">
        {result.receiver?.community &&
          result.expanded?.receiver.metadata.title && (
            <>
              <Icon
                className="default-margin"
                name={getUserIcon(result.expanded?.receiver)}
              />
              <span className="ml-5">
                {result.expanded?.receiver.metadata.title}
              </span>
            </>
          )}
        {result.expires_at && (
          <span>
            {i18next.t("Expires at: {{- expiringDate}}", {
              expiringDate: DateTime.fromISO(result.expires_at).toLocaleString(
                i18next.language
              ),
            })}
          </span>
        )}
      </small>
    </Item.Meta>
  );
};

ResultItemMeta.propTypes = {
  result: PropTypes.object.isRequired,
};
