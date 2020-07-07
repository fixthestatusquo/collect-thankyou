## Data processing overview

Data processing consist of:

- Widget where data is entered and passed on to Proca for processing
- AWS Lambda functions (in case of Reader(), it is run on heroku, because of lack of support in current Lambda runtime)
- S3 buckets, SQS queues are used to pass files and data

<PRE>
```
   +----------------+          ___________
   |                |         /           \
   |  Form          | =====> |  Proca API  | ========> [  SQS   ]
   |  Widget        |     .->|             |           [DELIVER ]
   |                |     |  |\___________/|           [        ]
   |                |     |  |  Database   |           [        ]
   +----------------+     |   \___________/            [________]
                          |    o-< actions  >              |
                          |    o-<supporters>              V
                          |    o-<campaigns >           Splitter()
                          |                               /  \ 
                          |                              /    \
                          |                  [identity-sync] [thank-you]
   -------.               |                     |              |
   | S3    |=>SNS->HTTP->Reader()               v              v                               
   |_______|                                IdentitySync()    ThankYou() <----- HTTP get email template from WP
     ^                                          |              |         <----- HTTP get PDF <=(PDF generator)
     |                                          v              v
   [SCANNER]                             Identoty DataApi     SES 
```
</PRE>

There are two workflows triggered by user action:

1. Member signs initiative on collect website. The widget uses Proca API
   (GraphQL addActionContact) call to create new action with action type
   "register", and provided member data. Proca creates a fingerprint unique for
   this campaign/member, encrypts personal information and sends the action data
   to SQS.

2. SQS deliver queue triggers lambda worker called _splitter_ that sends all
   action data to _identity_ queue, and also sents action data to _thankyou_
   queue, if action type is register.

3. The identity-sync SQS queue triggers identity sync lambda, which decrypts
   personal informatio nand sends actions to Identity. It must know the private
   key that is coupled with public key used to encrypt PII by Proca backend. It
   uses Identity API token to create actions.

4. The thank-you SQS queue triggers thankyou email sender, which a) fetches
   email template from WP, for page where the action was created, b) fetches the
   PDF form from generator, c) sends an email with attachment and link to
   member, using SES.
   
5. The other action is when a sent form is scanned and image file is created on S3. I triggers an SQS topic which is configured to call Reader() function. 


## Function projects

1. Splitter 

Receives actions from SQS, passes them to other SQS queues (identity and some to thank you)
Repo: https://github.com/marcinkoziej/collect-sqs-splitter

2. Identity Sync 

Receives actions, decrypts them and sends to Identity

Repo: https://github.com/marcinkoziej/identity-sync-lambda

3. Thank you sender

Fetches the postcard, fetches email template from Wordpress, builds email with attachment to send via SES.

Repo: https://github.com/marcinkoziej/collect-thankyou


4. Scan reader

Responds to SNS messages when new scanned image appears in S3 bucket, scans them, reads QRcode, estimates the number of handwritten signatures, and creats action for a member with type 'signature'

Repo: https://github.com/campaxadmin/collect-postcard-reader


## Setting up lambda functions

### Prerequisites

1. Set up aws cli. You need to configure it with `aws configure`
2. Create lambda functions using AWS console, remember to set policy for lambda runner so that it can access respective services (SQS, S3, SES)


### Building and deployment

In the project directory of function you want to deploy, run:

1. `./build.sh` to build the package. You can use `./build.sh -u` (update) to just update the `./src` files in the package. The resulting package will be called like the project directory with `.zip` appended.
2. `./deploy.sh function-name code-bucket-name` deploys the package to lambda function called function-name. Use the `code-bucket-name` to store the package file in the process.
3. `./configure.sh function-name env-file` use the env-file (by default env.json) to set up environment for lambda. You can also configure the lambda using AWS console UI. For each project you have a env.json.sample as an example

Check each project README.MD file for configuration description
