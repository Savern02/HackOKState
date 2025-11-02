# HackOKState
VolunTold:  Community outreach/volunteer app that connects college students to local community members in need

Venv:
```
.\venv\Scripts\activate
```

Migrate Database (do this whenever you edit the models):
```
set FLASK_APP=app
```

## Inspiration
>**Former Civic Hacking Projects:** We found inspiration from former projects that helped us make a difference it helped us _realize_ how we can make a impact that matters.

>**Lack of Volunteer Apps:** We couldn't think of a good way to find a volunteer opportunities  in our community, so we decided to make one.

>**Lots Of Redbull:** What can we say? We needed the _ENERGY_
## What it does
VolunTold has several features based on making and fostering  a community of VolunTold's users.

>**Gathering Volunteer Opportunities:** In the Discover tab you can select volunteer opportunities gathered by Google Gemini based on your location. This can work with any link, so we added a feature to get the community involved and share their local volunteer places.

>**Creating Volunteer Opportunities:** In the tab Opportunities, you can select volunteer opportunities that are exclusive to the web app. This allows organizations to post volunteer opportunities and in the future push users with important notifications for a important volunteer work needed after a crisis.

## How we built it
| Layer              | Technology                      | Description                                                         |
| ------------------ | ------------------------------- | ------------------------------------------------------------------- |
| **Frontend**       | 🧱 **Bootstrap**                | CSS framework for responsive, mobile-first UI design.               |
|                    | 🧩 **Flask Templates (Jinja2)** | Server-side rendering and dynamic HTML generation.                  |
| **Backend**        | 🐍 **Flask**                    | Lightweight Python web framework handling routes and APIs.          |
|                    | 🗃️ **SQLAlchemy**              | ORM providing structured access to the database.                    |
|                    | 💾 **SQLite**                   | Simple, file-based database for local persistence.                  |
| **Infrastructure** | 🐳 **Docker**                   | Containerization for consistent and portable app environments.      |
|                    | ☁️ **Vultr VM**                 | Cloud host running the Docker image with Flask and SQLite inside.   |
| **AI Integration** | 🤖 **Google Gemini with Open Router** | Powers the *Volunteer Gatherer* — AI for data parsing and matching. |

## Challenges we ran into
>**Framework Learning Curve:** It was our first time using these web frameworks to create an application

>**Environment Inconsistencies:** Local developer environments were somewhat inconsistent, especially with regards to database schemas at different points in development

>**Webscraping Limitations:** OpenAI API was misbheaving, and data retrieved was sometimes inconsistent, so we had to refine our original prompt and scope a bit in order for the webscraping module to work

## Accomplishments that we're proud of
> **AI Discover Feature** for creating summaries of possible volunteer opportunities given a website

> **Dockerization** for consistent builds and local developer environments (via docker-compose)

> **Framework** zero to hero over the course of the hackathon

## What we learned

> **LLM Interactions** using available web APIs

> **Flask backend** for quick and easy API's / webservers

> **Cloudflare** for domain resolution and secure site connections

## What's next for VolunTold

Try our docker-compose:

```yml
services:
  voluntold:
    image: ghcr.io/savern02/hackokstate:latest
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance # <-- you will need an sqlite database
    environment:
      OPEN_AI_KEY: "" # <-- fill with an OpenAPI key for the webscraping summaries
```

> Note: certificates for demo site set to expire a few days following the competition 
