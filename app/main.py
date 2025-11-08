from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import engine, get_db

app = FastAPI(title="Person Service API", version="1.0.0")


@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)


@app.get("/api/v1/persons", response_model=List[schemas.PersonResponse])
def list_persons(db: Session = Depends(get_db)):
    persons = db.query(models.Person).all()
    return persons


@app.get("/api/v1/persons/{person_id}", response_model=schemas.PersonResponse)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Person with id {person_id} not found"}
        )
    return person


@app.post("/api/v1/persons", status_code=status.HTTP_201_CREATED, response_model=schemas.PersonResponse)
def create_person(person: schemas.PersonRequest, response: Response, db: Session = Depends(get_db)):
    db_person = models.Person(**person.model_dump())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)

    response.headers["Location"] = f"/api/v1/persons/{db_person.id}"
    return db_person

@app.patch("/api/v1/persons/{person_id}", response_model=schemas.PersonResponse)
def update_person(person_id: int, person: schemas.PersonRequest, db: Session = Depends(get_db)):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if db_person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Person with id {person_id} not found"}
        )

    for key, value in person.model_dump(exclude_unset=True).items():
        setattr(db_person, key, value)

    db.commit()
    db.refresh(db_person)
    return db_person


@app.delete("/api/v1/persons/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if db_person is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    db.delete(db_person)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/manage/health")
def health_check():
    return {"status": "ok"}
