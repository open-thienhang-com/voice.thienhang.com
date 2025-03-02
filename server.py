#!/usr/bin/env python3

from src.utils.parse import parser

from src.services import Server
import uvicorn

app = Server().app
if __name__ == '__main__': 
    
   
    args = parser.parse_args()
    # if args.cors or True:
    #     app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=['*'],
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    # )

    uvicorn.run("server:app", host=args.host, port=args.port, log_level='info', reload=False)
    

   