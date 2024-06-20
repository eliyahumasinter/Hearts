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
The current presentation layer is a text-based UI. A server allows users to connect, and then it will start games in different threads to allow users to play concurrently. Note that the server is technically part of the presentation layer because it is only responsible for displaying info to each user; it does not do any gameplay logic.

![image](https://github.com/eliyahumasinter/Hearts/assets/70181151/a5857851-9fc6-4b5d-86be-9cdadd2c99dd)
command line version mentioned above

## Current project status
The logical layer is nearly complete. More unit and integration tests must be written, but the functionality is almost all there. 

I have implemented the structure necessary to allow 'bots' to play allowing for games with fewer than 4 people. At the moment, the bot just chooses the first card that it is allowed to play. Obviously, this needs to be improved on. Once the server handling all of the sockets and threading is completed and polished I will use it as a base for another presentation layer using pygame. I hope to eventually host this project and build a web interface to allow users to connect online instead of downloading the client.
