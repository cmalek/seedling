#################################################################
# Multitenant Config
#################################################################
from environs import Env

env = Env()
env.read_env()

# Do not log changes to the following models. The model's full app_label.ModelName string must be included.
UNLOGGED_MODELS = ['sessions.Session']

# Allow only bold, italics, and linebreak tags in bleach-filtered outputs.
# Devs can use the custom_bleach filter from jetstream_tags to apply alternate tag restrictions.
BLEACH_ALLOWED_TAGS = ['b', 'i', 'em', 'strong', 'br']
