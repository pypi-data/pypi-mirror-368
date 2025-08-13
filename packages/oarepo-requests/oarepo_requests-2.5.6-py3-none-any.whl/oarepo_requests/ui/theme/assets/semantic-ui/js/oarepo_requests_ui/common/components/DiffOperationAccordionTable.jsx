import React, { useState } from "react";
import PropTypes from "prop-types";
import { Icon, Table, Accordion } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import {
  formatValueToStringLikeFormat,
  formatNestedRecordFieldPath,
} from "@js/oarepo_requests_common";

export const DiffOperationAccordionTable = ({ operations, operationType }) => {
  const [isAccordionVisible, setIsAccordionVisible] = useState(false);

  const operationConfig = {
    add: {
      title: i18next.t("Added"),
      icon: "add",
      color: "green"
    },
    remove: {
      title: i18next.t("Removed"),
      icon: "remove",
      color: "red"
    },
    replace: {
      title: i18next.t("Changed"),
      icon: "pencil",
      color: "orange"
    }
  };

  const config = operationConfig[operationType];
  if (!config || operations.length === 0) return null;

  return (
    <Accordion key={operationType} fluid className={`operation-accordion ${operationType} rel-mb-1`}>
      <Accordion.Title
        active={isAccordionVisible}
        onClick={() => setIsAccordionVisible(!isAccordionVisible)}
        className={`operation-title ${operationType} flex align-items-center`}
      >
        <Icon name="dropdown" />
        <span>
          <Icon name={config.icon} className="operation-icon" />
          {config.title}
          <span className="operation-count">({operations.length})</span>
        </span>
      </Accordion.Title>
      <Accordion.Content active={isAccordionVisible}>
        <Table basic celled stackable className={`record-diff-table requests ${operationType} borderless`}>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell>{i18next.t("Field")}</Table.HeaderCell>
              {operationType === "replace" ? (
                <>
                  <Table.HeaderCell>{i18next.t("Old Value")}</Table.HeaderCell>
                  <Table.HeaderCell>{i18next.t("New Value")}</Table.HeaderCell>
                </>
              ) : (
                <Table.HeaderCell>{i18next.t("Value")}</Table.HeaderCell>
              )}
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {operations.map((op, index) => (
              <Table.Row key={`${operationType}-${index}`}>
                <Table.Cell>
                  <code>{formatNestedRecordFieldPath(op.path)}</code>
                </Table.Cell>
                {operationType === "replace" ? (
                  <>
                    <Table.Cell>
                      <pre>{formatValueToStringLikeFormat(op.old_value)}</pre>
                    </Table.Cell>
                    <Table.Cell>
                      <pre>{formatValueToStringLikeFormat(op.value)}</pre>
                    </Table.Cell>
                  </>
                ) : (
                  <Table.Cell>
                    <pre>{formatValueToStringLikeFormat(operationType === "remove" ? op.old_value : op.value)}</pre>
                  </Table.Cell>
                )}
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </Accordion.Content>
    </Accordion>
  );
};

DiffOperationAccordionTable.propTypes = {
  operations: PropTypes.arrayOf(
    PropTypes.shape({
      op: PropTypes.string.isRequired,
      path: PropTypes.string.isRequired,
      old_value: PropTypes.any,
      value: PropTypes.any,
    })
  ).isRequired,
  operationType: PropTypes.oneOf(["add", "remove", "replace"]).isRequired,
};
