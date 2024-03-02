import asyncio
from beanie import PydanticObjectId
from fastapi import APIRouter, Request, status
from client.response import CustomResponse
from repository.candidate import CandidateRepository
from repository.elections import ElectionRepository
from repository.student import StudentRepository
from repository.vote import VoteRepository
from utils.query import VoteSchema
from exceptions.custom_exception import BadRequestException


router = APIRouter(tags=["Elections"], prefix="/election")


@router.get("/{election_id}/candidate")
async def get_candidates_for_election(request: Request, election_id: PydanticObjectId):

    if not await ElectionRepository.does_election_exists(election_id):
        raise BadRequestException("this election doesn't exists")

    candidates = await CandidateRepository.get_all_candidate_on_election(election_id)

    context = {"candidates": [candidate.to_dict() for candidate in candidates]}

    return CustomResponse(
        "all candidates", data=context, status=status.HTTP_201_CREATED
    )


@router.get("/verify_voter/{voiting_number}")
async def verify_voter(request: Request, voting_number: str):

    student = await StudentRepository.get_student_by_voting_number(voting_number)

    if not student:
        raise BadRequestException("this student doesn't exist")

    context = {"student": student.to_dict()}

    return CustomResponse("verified student", data=context)


@router.post("/vote")
async def vote_for_candidate(
    request: Request,
    vote_input: VoteSchema,
):

    tasks = [
        StudentRepository.get_student_by_voting_number(vote_input.voting_number),
        ElectionRepository.does_election_exists(vote_input.election_id),
        CandidateRepository.does_candidate_exist(vote_input.candidate_id),
    ]

    (
        student,
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
