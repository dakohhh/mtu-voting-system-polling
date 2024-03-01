import asyncio
from beanie import PydanticObjectId
from pydantic import EmailStr
from fastapi import APIRouter, Depends, Request, BackgroundTasks, status
from authentication.auth import Auth
from authentication.hashing import checkPassword, hashPassword
from client.response import CustomResponse
from database.schema import Student
from repository.candidate import CandidateRepository
from repository.department import DepartmentRepository
from repository.elections import ElectionRepository
from repository.otp import OTPRespository
from repository.student import StudentRepository
from repository.vote import VoteRepository
from utils.func import generate_random_otp
from utils.query import SignupSchema, VoteSchema
from exceptions.custom_exception import BadRequestException
from utils.task import send_otp_mail


router = APIRouter(tags=["Elections"], prefix="/elections")


auth = Auth()



@router.get("/election/{id}")
async def get_candidates_on_elections(
    request: Request,
    id: PydanticObjectId,
    student: Student = Depends(auth.get_current_student),
):

    if not await ElectionRepository.does_election_exists(id):

        raise BadRequestException("this election doesn't exists")

    candidates = await CandidateRepository.get_all_candidate_on_election(id)

    context = {"candidates": [candidate.to_dict() for candidate in candidates]}

    return CustomResponse("get candidates for election", data=context)


@router.post("/election/vote")
async def vote_for_candidate(
    request: Request,
    vote_input: VoteSchema,
    student: Student = Depends(auth.get_current_student),
):
    tasks = [
        ElectionRepository.does_election_exists(vote_input.election_id),
        CandidateRepository.does_candidate_exist(vote_input.candidate_id),
    ]

    (
        election_exists,
        candidate_exists,
    ) = await asyncio.gather(*tasks)

    

    if not election_exists:
        raise BadRequestException("this election doesn't exists")
    

    if not candidate_exists:
        raise BadRequestException("this candidate doesn't exists")
    
    
    if await VoteRepository.has_voted_for_election(student, vote_input.election_id):
        raise BadRequestException("you have voted on this election already")
    

    vote = await VoteRepository.vote_for_candidate(student, vote_input)


    return CustomResponse("vote for candidate successfuly", data=None)

    