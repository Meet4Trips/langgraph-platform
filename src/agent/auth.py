import os
from venv import logger
import jwt
import base64
import time
from langgraph_sdk import Auth

supabase_jwt_auth = Auth()

@supabase_jwt_auth.authenticate
async def authenticate(authorization: str) -> str:
    token = authorization.split(" ", 1)[-1] # "Bearer <token>"
    try:
        # Verify token with your auth provider
        user_id = verify_token(token)
        if not user_id:
            raise Auth.exceptions.HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        return user_id
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise Auth.exceptions.HTTPException(
            status_code=401,
            detail="Invalid token"
        )

# Add authorization rules to actually control access to resources
@supabase_jwt_auth.on
async def add_owner(
    ctx: Auth.types.AuthContext,
    value: dict,
):
    """Add owner to resource metadata and filter by owner."""
    filters = {} if ctx.resource == "assistants" else {"owner": ctx.user.identity}
    metadata = value.setdefault("metadata", {})
    metadata.update(filters)
    return filters

# Assumes you organize information in store like (user_id, resource_type, resource_id)
@supabase_jwt_auth.on.store()
async def authorize_store(ctx: Auth.types.AuthContext, value: dict):
    namespace: tuple = value["namespace"]
    assert namespace[0] == ctx.user.identity, "Not authorized"

def verify_token(token: str) -> str:
    JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")
    if not JWT_SECRET:
        logger.error("JWT_SECRET is not set in environment variables")
        return None
    
    ALGORITHM = "HS256"
    try:
        decoded = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=ALGORITHM,
            audience="authenticated",  # Or your audience string, if set
        )
        # logger.info("✅ JWT is valid! for user: " + decoded.get('email') or decoded.get('sub'))
        #logger.info(f"Decoded token: {decoded}")

        # Check if token is expired
        current_time = int(time.time())
        if decoded.get('exp', 0) < current_time:
            logger.error("❌ Token has expired")
            return None

        # Check if user is anonymous
        if decoded.get('is_anonymous', False):
            logger.error("❌ Anonymous users are not allowed")
            return None

        # Return the user ID from the decoded token
        return decoded.get('sub') or decoded.get('email')
    except jwt.InvalidTokenError as e:
        logger.error(f"❌ Invalid token: {str(e)}")
        return None 