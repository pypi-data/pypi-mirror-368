import React from "react";
import { RichEditor } from "react-invenio-forms";
import sanitizeHtml from "sanitize-html";
import PropTypes from "prop-types";
import { useQuery } from "@tanstack/react-query";
import { httpApplicationJson } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import Overridable from "react-overridable";
import { MAX_COMMENT_LENGTH } from "@js/oarepo_requests_common";
import { Icon } from "semantic-ui-react";

const CommentInput = ({
  comment,
  handleChange,
  initialValue,
  length,
  setLength,
  maxCommentLength,
}) => {
  // when focused move the cursor at the end of any existing content
  const handleFocus = (event, editor) => {
    editor.selection.select(editor.getBody(), true);
    editor.selection.collapse(false);
  };
  // TODO: there is no appropriate URL to call here. I think this one is the safest, because we know it exists and it does
  // not rely on external library (like those that contain /me that are from dashboard). To be discussed how to handle this appropriately.
  // maybe some link that lives in oarepo ui and that can universaly provide allowed tags and attributes
  const { data } = useQuery(
    ["allowedHtmlTagsAttrs"],
    () => httpApplicationJson.get(`/requests/configs/publish_draft`),
    {
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    }
  );

  const allowedHtmlAttrs = data?.data?.allowedHtmlAttrs;
  const allowedHtmlTags = data?.data?.allowedHtmlTags;

  return (
    <Overridable
      id="OarepoRequests.RequestCommentInput"
      comment={comment}
      handleChange={handleChange}
      initialValue={initialValue}
      maxCommentLength={maxCommentLength}
    >
      <React.Fragment>
        <RichEditor
          initialValue={initialValue}
          inputValue={comment}
          editorConfig={{
            auto_focus: true,
            min_height: 100,
            width: "100%",
            entity_encoding: "raw",
            toolbar:
              "blocks | bold italic | bullist numlist | outdent indent | undo redo",
            setup: (editor) => {
              editor.on("BeforeAddUndo", (event) => {
                const length = editor.getContent({ format: "text" }).length;
                if (length >= maxCommentLength) {
                  event.preventDefault();
                }
              });
              editor.on("init", () => {
                setLength(editor.getContent({ format: "text" }).length);
              });
            },
          }}
          onEditorChange={(event, editor) => {
            const cleanedContent = sanitizeHtml(editor.getContent(), {
              allowedTags: allowedHtmlTags,
              allowedAttributes: allowedHtmlAttrs,
            });
            const textContent = editor.getContent({ format: "text" });
            const textLength = textContent.length;
            handleChange(event, cleanedContent);
            // querky  behavior of the editor, when the content is empty, the length is 1
            if (textContent.trim().length === 0 && textContent.length <= 1) {
              setLength(0);
            } else {
              setLength(textLength);
            }
          }}
          onFocus={handleFocus}
        />
        {length <= maxCommentLength ? (
          <small>{`${i18next.t("Remaining characters: ")}${
            maxCommentLength - length
          }`}</small>
        ) : (
          <small>
            <Icon name="warning circle" color="red" />
            {i18next.t("commentTooLong", { count: length - maxCommentLength })}
          </small>
        )}
      </React.Fragment>
    </Overridable>
  );
};

export const RequestCommentInput = Overridable.component(
  "RequestCommentInput",
  CommentInput
);

CommentInput.propTypes = {
  comment: PropTypes.string,
  handleChange: PropTypes.func,
  initialValue: PropTypes.string,
  length: PropTypes.number,
  setLength: PropTypes.func,
  maxCommentLength: PropTypes.number,
};

CommentInput.defaultProps = {
  initialValue: "",
  maxCommentLength: MAX_COMMENT_LENGTH,
};
