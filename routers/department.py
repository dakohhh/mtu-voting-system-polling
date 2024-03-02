from beanie import PydanticObjectId
from bson import ObjectId
from fastapi import APIRouter, Request, status
from authentication.auth import Auth
from database.schema import Department
from client.response import CustomResponse
from repository.department import DepartmentRepository
from repository.elections import ElectionRepository
from utils.query import LoginSchema, DepartmentSchema
from exceptions.custom_exception import BadRequestException


router = APIRouter(tags=["Department"], prefix="/department")


auth = Auth()


@router.get("/")
async def get_all_departments(request: Request):

    departments = await DepartmentRepository.get_all_departments()

    context = {"departments": [department.to_dict() for department in departments]}

    return CustomResponse("all departments", data=context)


@router.post("/create")
async def create_department(
    request: Request, secret: str, department_input: DepartmentSchema
):

    if secret != "wisdom12":
        raise BadRequestException("invalid secret")

    department = await DepartmentRepository.create_department(department_input)

    context = {"department": department.to_dict()}

    return CustomResponse("created department successfully", data=context)


@router.get("/{department_id}/elections")
async def get_all_elections_in_department(
    request: Request, department_id: PydanticObjectId
):

    if not await DepartmentRepository.does_department_exist(department_id):

        raise BadRequestException("this department doesn't exist")

    
    elections = await ElectionRepository.get_all_elections(department_id)

    context = {"elections": [election.to_dict() for election in elections]}

    return CustomResponse("all elections for the department", data=context)
