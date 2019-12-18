import sklearn.cluster, discord, io
from config import config
import numpy as np
from PIL import Image

client = discord.Client()

def dominant_color(image, seed=0, samples=1000):
    """Finds the dominant color by clustering an image.

    Args:
        image: An array-like of pixels, where the last dimension is the
            components of the image.
        seed: The seed for the random generator.
        samples: the number of samples to pass to clustering.

    Returns:
        A numpy array, shape (image.shape[-1],) representing the dominant
        color in the image.
    """

    image = np.ascontiguousarray(image)
    image = image.reshape((-1, image.shape[-1]))

    np.random.seed(seed)
    indices = np.random.randint(image.shape[0], size=samples)
    image = image[indices]

    kmeans = sklearn.cluster.KMeans(n_clusters=10, random_state=0)
    centers = kmeans.fit(image).cluster_centers_
    return centers[0]

def get_color_role(user):
    for role in reversed(user.roles):
        if role.colour.value:
            return role

async def update_role_color(role, color, proxy_member):
    # Fine to use guild permissions as channels cannot override manage roles
    if not proxy_member.guild_permissions.manage_roles:
        return False
    elif proxy_member.top_role <= role:
        return False
    else:
        await role.edit(color=color)
        return True

def get_embed(role, old_color, new_color, member):
    return discord.Embed(color=new_color, description=f"{member.mention}, "
        f"I changed the color of role \"{role.mention}\" "
        f"from `#{old_color.value:06x}` to `#{new_color.value:06x}`")

@client.event
async def on_ready():
    print(client.user)

@client.event
async def on_message(message):
    # Ignore messages which don't mention us
    try:
        i = message.mentions.index(client.user)
    except ValueError:
        return

    # Choose user to target
    proxy_member = message.author
    if len(message.mentions) > 1:
        target_member = message.mentions[(i+1) % len(message.mentions)]
    else:
        target_member = message.author

    # Make sure both target user and proxy user are in the server
    if not isinstance(target_member, discord.Member) \
            or not isinstance(proxy_member, discord.Member):
        await message.channel.send(f"{target_member.mention}, "
            "you and the target user must be in the same server.")
        return

    # Download target avatar
    f = io.BytesIO()
    await target_member.avatar_url_as().save(f)
    image = Image.open(f)

    # Update role to dominant color
    role = get_color_role(target_member)
    color = np.round(dominant_color(image)).astype(int).tolist()
    color = discord.Color.from_rgb(*color)

    old_color = role.color
    if await update_role_color(role, color, proxy_member):
        embed = get_embed(role, old_color, color, proxy_member)
        await message.channel.send(embed=embed)
    else:
        await message.channel.send(f"{proxy_member.mention}, "
            "you don't have permission to do that.")

if __name__ == "__main__":
    client.run(config["Tokens"]["sam"])
