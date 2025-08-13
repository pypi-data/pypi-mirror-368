import React, { useState } from "react";
import { i18next } from "@translations/oarepo_requests_ui/i18next";
import { Feed, Dropdown, Button, Confirm, Message } from "semantic-ui-react";
import _has from "lodash/has";
import sanitizeHtml from "sanitize-html";
import PropTypes from "prop-types";
import { toRelativeTime, Image } from "react-invenio-forms";
import {
  ConfirmationModalCancelButton,
  ConfirmationModalConfirmButton,
  RequestCommentInput,
  MAX_COMMENT_LENGTH,
} from "@js/oarepo_requests_common";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { httpApplicationJson } from "@js/oarepo_ui";

const TimelineCommentEvent = ({ event, requestId, page }) => {
  const createdBy = event?.expanded?.created_by;
  const creatorLabel =
    createdBy?.profile?.full_name || createdBy?.username || createdBy?.email;
  const [editMode, setEditMode] = useState(false);
  const [deleteMode, setDeleteMode] = useState(false);
  const [comment, setComment] = useState(event.payload.content);
  const [length, setLength] = useState(comment.length);
  const handleLengthChange = (length) => setLength(length);
  const toggleEditMode = () => setEditMode(!editMode);
  const toggleDeleteMode = () => setDeleteMode(!deleteMode);
  const canUpdate = event?.permissions?.can_update_comment;
  const canDelete = event?.permissions?.can_delete_comment;
  const commentHasBeenEdited = event?.revision_id > 1 && event?.payload;
  const queryClient = useQueryClient();
  const {
    mutate: editComment,
    isLoading: editLoading,
    isError: editError,
    reset: resetEditCommentMutation,
  } = useMutation(({ url, values }) => httpApplicationJson.put(url, values), {
    onSuccess: (response) => {
      queryClient.setQueryData(
        ["requestEvents", requestId, page],
        (oldData) => {
          if (!oldData) return;
          // a bit ugly, but it is a limitation of react query when data you recieve is nested
          const newHits = [...oldData.data.hits.hits];
          const commentIndex = newHits.findIndex(
            (comment) => comment.id === response.data.id
          );
          newHits[commentIndex] = response.data;

          return {
            ...oldData,
            data: {
              ...oldData.data,
              hits: {
                ...oldData.data.hits,
                hits: newHits,
              },
            },
          };
        }
      );
      setTimeout(
        () => queryClient.invalidateQueries(["requestEvents", requestId, page]),
        1000
      );
    },
  });

  const {
    mutate: deleteComment,
    isLoading: deleteLoading,
    isError: deleteError,
    reset: resetDeleteCommentMutation,
  } = useMutation(({ url }) => httpApplicationJson.delete(url), {
    onSuccess: (response, variables) => {
      const { eventId } = variables;
      queryClient.setQueryData(
        ["requestEvents", requestId, page],
        (oldData) => {
          if (!oldData) return;
          // a bit ugly, but it is a limitation of react query when data you recieve is nested
          const newHits = [...oldData.data.hits.hits];
          const indexCommentToDelete = newHits.findIndex(
            (comment) => comment.id === eventId
          );

          const currentComment = newHits[indexCommentToDelete];

          const deletionPayload = {
            content: i18next.t("deleted comment"),
            event: "comment_deleted",
            format: "html",
          };

          newHits[indexCommentToDelete] = {
            ...currentComment,
            type: "L",
            payload: deletionPayload,
          };
          return {
            ...oldData,
            data: {
              ...oldData.data,
              hits: {
                ...oldData.data.hits,
                hits: newHits,
              },
            },
          };
        }
      );
      setTimeout(
        () => queryClient.invalidateQueries(["requestEvents", requestId, page]),
        1000
      );
    },
  });

  const handleEditComment = () => {
    editComment(
      {
        url: event.links.self + "?expand=1",
        values: { payload: { content: comment, format: "html" } },
      },
      // timeout necessary to avoid showing previous comment for a moment
      {
        onSuccess: () => setTimeout(() => setEditMode(false), 200),
        onError: () => {
          setTimeout(() => resetEditCommentMutation(), 3000);
        },
      }
    );
  };

  const handleConfirmDeletion = () => {
    deleteComment(
      { url: event.links.self, eventId: event.id },
      {
        onSettled: () => setDeleteMode(false),
        onError: () => setTimeout(() => resetDeleteCommentMutation(), 3000),
      }
    );
  };

  const handleCancelDeletion = () => {
    setDeleteMode(false);
  };

  const handleCommentChange = (event, value) => {
    setComment(value);
  };

  const editButtonDisabled =
    editLoading ||
    comment === event.payload.content ||
    !comment ||
    length > MAX_COMMENT_LENGTH;
  return (
    <div className="requests comment-event-container">
      <Feed.Event key={event.id}>
        {createdBy?.links?.avatar && (
          <div className="requests comment-event-avatar">
            <Image
              src={createdBy?.links?.avatar}
              alt={i18next.t("User avatar")}
            />
          </div>
        )}
        <Feed.Content>
          <Feed.Summary>
            <b>{creatorLabel}</b>
            <Feed.Date>
              {i18next.t("requestCommented")}{" "}
              {toRelativeTime(event.created, i18next.language)}
            </Feed.Date>
            {(canDelete || canUpdate) && (
              <Dropdown
                icon="ellipsis horizontal"
                className="right-floated"
                direction="left"
                aria-label={i18next.t("Actions")}
              >
                <Dropdown.Menu>
                  {canUpdate && (
                    <Dropdown.Item onClick={() => toggleEditMode()}>
                      {i18next.t("Edit")}
                    </Dropdown.Item>
                  )}
                  {canDelete && (
                    <Dropdown.Item onClick={() => toggleDeleteMode()}>
                      {i18next.t("Delete")}
                    </Dropdown.Item>
                  )}
                </Dropdown.Menu>
              </Dropdown>
            )}
          </Feed.Summary>
          {_has(event.payload, "content") && !editMode && (
            <Feed.Extra text>
              <div
                dangerouslySetInnerHTML={{
                  __html: sanitizeHtml(event.payload.content),
                }}
              />
            </Feed.Extra>
          )}
          {editMode && (
            <React.Fragment>
              <RequestCommentInput
                comment={comment}
                initialValue={event?.payload?.content}
                handleChange={handleCommentChange}
                length={length}
                setLength={handleLengthChange}
                maxCommentLength={MAX_COMMENT_LENGTH}
              />
              <div className="requests edit-comment-buttons">
                <Button
                  icon="close"
                  type="button"
                  labelPosition="left"
                  size="tiny"
                  onClick={toggleEditMode}
                  content={i18next.t("Cancel")}
                />
                <Button
                  icon="save"
                  type="button"
                  primary
                  labelPosition="left"
                  size="tiny"
                  disabled={editButtonDisabled}
                  loading={editLoading}
                  onClick={handleEditComment}
                  content={i18next.t("Save")}
                />
              </div>
            </React.Fragment>
          )}
          {editError && (
            <Message negative>
              <Message.Header>
                {i18next.t(
                  "Comment was not edited successfully. Please try again in a moment."
                )}
              </Message.Header>
            </Message>
          )}
          {deleteError && (
            <Message negative>
              <Message.Header>
                {i18next.t(
                  "Comment was not deleted successfully. Please try again in a moment."
                )}
              </Message.Header>
            </Message>
          )}
          {commentHasBeenEdited && (
            <Feed.Meta>
              {i18next.t("Edited")}{" "}
              {toRelativeTime(event.updated, i18next.language)}
            </Feed.Meta>
          )}
        </Feed.Content>
      </Feed.Event>
      <Confirm
        className="requests dangerous-action-confirmation-modal "
        open={deleteMode}
        onCancel={handleCancelDeletion}
        onConfirm={handleConfirmDeletion}
        confirmButton={
          <ConfirmationModalConfirmButton
            negative
            labelPosition="left"
            icon="trash"
            content={i18next.t("Delete comment")}
            disabled={deleteLoading}
            loading={deleteLoading}
          />
        }
        cancelButton={
          <ConfirmationModalCancelButton
            labelPosition="left"
            icon="close"
            content={i18next.t("Cancel")}
          />
        }
        content={i18next.t("Are you sure you want to delete this comment?")}
      />
      <div className="comment-event-vertical-line"></div>
    </div>
  );
};

TimelineCommentEvent.propTypes = {
  event: PropTypes.object.isRequired,
  requestId: PropTypes.string.isRequired,
  page: PropTypes.number.isRequired,
};
export default TimelineCommentEvent;
