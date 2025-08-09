#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Class for milestone model in RegScale platform"""

from typing import Optional
from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class Milestone(RegScaleModel):
    """Milestone Model"""

    _module_slug = "milestones"
    _module_string = "milestones"

    title: str
    id: int = 0
    isPublic: Optional[bool] = True
    milestoneDate: Optional[str] = Field(default_factory=get_current_datetime)
    responsiblePersonId: Optional[str] = None
    predecessorStepId: Optional[int] = 0
    completed: Optional[bool] = False
    dateCompleted: Optional[str] = Field(default_factory=get_current_datetime)
    notes: Optional[str] = ""
    parentID: Optional[int] = None
    parentModule: str = ""

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Milestone model

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}",
        )
