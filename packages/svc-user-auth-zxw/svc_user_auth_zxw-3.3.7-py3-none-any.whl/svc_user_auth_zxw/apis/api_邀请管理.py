"""
# File       : api_邀请管理.py
# Time       ：2024/12/19
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：邀请管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.db.models import User
from svc_user_auth_zxw.interface.invitation_interface import InvitationInterface
from svc_user_auth_zxw.apis.schemas import (
    通用响应, 邀请汇总信息响应, 用户邀请人响应, 邀请统计信息响应,
    邀请用户信息, 获取邀请列表请求
)
from svc_user_auth_zxw.apis.api_JWT import get_current_user
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_user_auth_zxw.tools.error_code import ErrorCode

router = APIRouter(prefix="/invitation", tags=["邀请管理"])


@router.get("/summary/{user_id}", response_model=通用响应[邀请汇总信息响应])
async def 获取用户邀请汇总(
    # user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户邀请汇总信息

    - **user_id**: 用户ID
    - 返回用户的邀请人信息、邀请数量、被邀请用户列表等汇总信息
    """
    try:
        # 创建邀请接口实例
        invitation_interface = InvitationInterface(db)

        # 获取邀请汇总信息
        summary_data = await invitation_interface.get_invitation_summary(current_user.id)

        return 通用响应[邀请汇总信息响应](
            code=200,
            data=邀请汇总信息响应(**summary_data),
            message="获取邀请汇总信息成功"
        )

    except ValueError as ve:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.参数验证失败,
            detail=str(ve),
            http_status_code=400
        )
    except Exception as e:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.数据查询失败,
            detail=f"获取邀请汇总信息失败: {str(e)}",
            http_status_code=500
        )


@router.get("/invitees/{user_id}", response_model=通用响应[List[邀请用户信息]])
async def 获取用户邀请列表(
    # user_id: int,
    limit: Optional[int] = Query(10, description="限制返回数量", ge=1, le=100),
    offset: int = Query(0, description="偏移量", ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户邀请的用户列表

    - **user_id**: 邀请人用户ID
    - **limit**: 限制返回数量 (1-100)
    - **offset**: 分页偏移量
    """
    try:
        # 创建邀请接口实例
        invitation_interface = InvitationInterface(db)

        # 获取邀请用户列表
        invitees_data = await invitation_interface.get_user_invitees(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )

        # 转换为响应模型
        invitees_list = [邀请用户信息(**invitee) for invitee in invitees_data]

        return 通用响应[List[邀请用户信息]](
            code=200,
            data=invitees_list,
            message=f"获取邀请列表成功，共{len(invitees_list)}条记录"
        )

    except ValueError as ve:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.参数验证失败,
            detail=str(ve),
            http_status_code=400
        )
    except Exception as e:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.数据查询失败,
            detail=f"获取邀请列表失败: {str(e)}",
            http_status_code=500
        )


@router.get("/count/{user_id}", response_model=通用响应[int])
async def 获取用户邀请数量(
    # user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户邀请的用户数量

    - **user_id**: 邀请人用户ID
    """
    try:
        # 创建邀请接口实例
        invitation_interface = InvitationInterface(db)

        # 获取邀请数量
        count = await invitation_interface.get_invitation_count(current_user.id)

        return 通用响应[int](
            code=200,
            data=count,
            message=f"用户{current_user.id}共邀请了{count}个用户"
        )

    except ValueError as ve:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.参数验证失败,
            detail=str(ve),
            http_status_code=400
        )
    except Exception as e:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.数据查询失败,
            detail=f"获取邀请数量失败: {str(e)}",
            http_status_code=500
        )


@router.get("/referrer/{user_id}", response_model=通用响应[Optional[用户邀请人响应]])
async def 获取用户邀请人(
    # user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户的邀请人信息

    - **user_id**: 被邀请用户ID
    - 如果用户没有邀请人，返回null
    """
    try:
        # 创建邀请接口实例
        invitation_interface = InvitationInterface(db)

        # 获取邀请人信息
        referrer_data = await invitation_interface.get_user_referrer(current_user.id)

        if referrer_data is None:
            return 通用响应[Optional[用户邀请人响应]](
                code=200,
                data=None,
                message=f"用户{current_user.id}没有邀请人"
            )

        return 通用响应[Optional[用户邀请人响应]](
            code=200,
            data=用户邀请人响应(**referrer_data),
            message="获取邀请人信息成功"
        )

    except ValueError as ve:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.参数验证失败,
            detail=str(ve),
            http_status_code=400
        )
    except Exception as e:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.数据查询失败,
            detail=f"获取邀请人信息失败: {str(e)}",
            http_status_code=500
        )


@router.get("/statistics/{user_id}", response_model=通用响应[邀请统计信息响应])
async def 获取邀请统计信息(
    # user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户邀请统计信息

    - **user_id**: 用户ID
    - 包括直接邀请数量、二级邀请数量等统计信息
    """
    try:
        # 创建邀请接口实例
        invitation_interface = InvitationInterface(db)

        # 获取邀请统计信息
        statistics_data = await invitation_interface.get_invitation_statistics(current_user.id)

        return 通用响应[邀请统计信息响应](
            code=200,
            data=邀请统计信息响应(**statistics_data),
            message="获取邀请统计信息成功"
        )

    except ValueError as ve:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.参数验证失败,
            detail=str(ve),
            http_status_code=400
        )
    except Exception as e:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.数据查询失败,
            detail=f"获取邀请统计信息失败: {str(e)}",
            http_status_code=500
        )


@router.get("/my-summary", response_model=通用响应[邀请汇总信息响应])
async def 获取当前用户邀请汇总(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前登录用户的邀请汇总信息

    - 需要用户认证
    - 自动获取当前登录用户的邀请信息
    """
    try:
        # 创建邀请接口实例
        invitation_interface = InvitationInterface(db)

        # 获取当前用户的邀请汇总信息
        summary_data = await invitation_interface.get_invitation_summary(current_user.id)

        return 通用响应[邀请汇总信息响应](
            code=200,
            data=邀请汇总信息响应(**summary_data),
            message="获取个人邀请汇总信息成功"
        )

    except ValueError as ve:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.参数验证失败,
            detail=str(ve),
            http_status_code=400
        )
    except Exception as e:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.数据查询失败,
            detail=f"获取个人邀请汇总信息失败: {str(e)}",
            http_status_code=500
        )
