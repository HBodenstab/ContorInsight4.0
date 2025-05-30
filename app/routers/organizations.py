from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.database import get_supabase
from app.models.schemas import Organization, OrganizationCreate

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.get("/", response_model=List[Organization])
async def list_organizations(supabase = Depends(get_supabase)):
    result = supabase.table("organizations").select("*").execute()
    if not result.data:
        return []
    return [Organization(**org) for org in result.data]

@router.post("/", response_model=Organization)
async def create_organization(org: OrganizationCreate, supabase = Depends(get_supabase)):
    result = supabase.table("organizations").insert({"name": org.name}).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create organization")
    return Organization(**result.data[0])

@router.get("/{organization_id}", response_model=Organization)
async def get_organization(organization_id: str, supabase = Depends(get_supabase)):
    response = supabase.table("organizations").select("*").eq("id", organization_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Organization not found")
    return Organization(**response.data[0])

@router.put("/{organization_id}", response_model=Organization)
async def update_organization(organization_id: str, organization: OrganizationCreate, supabase = Depends(get_supabase)):
    response = supabase.table("organizations").update(organization.dict()).eq("id", organization_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Organization not found")
    return Organization(**response.data[0])

@router.delete("/{organization_id}")
async def delete_organization(organization_id: str, supabase = Depends(get_supabase)):
    response = supabase.table("organizations").delete().eq("id", organization_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {"message": "Organization deleted successfully"} 