from environs import Env

env = Env()
env.read_env()

XFF_TRUSTED_PROXY_DEPTH = env.int('XFF_TRUSTED_PROXY_DEPTH', 0)
XFF_HEADER_REQUIRED = env.bool('XFF_HEADER_REQUIRED', False)

