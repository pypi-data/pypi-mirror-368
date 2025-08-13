import { LabelStatusCreate } from "./labels/TypeLabels";
import {
  PublishRecordIcon,
  DeleteRecordIcon,
  EditRecordIcon,
  RecordNewVersionIcon,
  AssignDoiIcon,
} from "./icons/TypeIcons";

export const requestTypeSpecificComponents = {
  [`InvenioRequests.RequestTypeIcon.layout.edit_published_record`]:
    EditRecordIcon,
  [`InvenioRequests.RequestTypeIcon.layout.delete_published_record`]:
    DeleteRecordIcon,
  [`InvenioRequests.RequestTypeIcon.layout.publish_draft`]: PublishRecordIcon,
  PublishRecordIcon,
  [`InvenioRequests.RequestTypeIcon.layout.new_version`]: RecordNewVersionIcon,
  [`InvenioRequests.RequestTypeIcon.layout.assign_doi`]: AssignDoiIcon,
  [`RequestStatusLabel.layout.created`]: LabelStatusCreate,
};
