# Hearts - _The Classic Card Game_



This project is split into three disjoint parts
- The Logical layer
- The API
- The Presentation Layer


#### The Logical Layer
The game state and rules of play are defined here.

#### The API 
The API connects between the Logical Layer and the Presentation Layer. It allows any number of frontends to be used with no modifications needed to the logical layer. 

#### The Presentation Layer
The presentation layer never talks to the logical layer. It interacts solely through the API. It does this by setting hooks/callbacks that the API can validate and then use in the logical layer.

## Current project status
The logical layer is nearly complete. More unit and integration tests must be written, but the functionality is almost all there. Additionally, I'd like to build an AI to play so a single user can play.

The API needs its own suite of tests written. There are a few more hooks that need to be included.

The presentation layer needs to be created. I'd like to build a few different ones. I created a terminal presentation layer, but of course that is just for testing. I hope to build a multi-player pygame front end that works over sockets. Perhaps a similar React web app.
