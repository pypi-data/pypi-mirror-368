# Profit

Types:

```python
from fv.types import ProfitCalculateResponse
```

Methods:

- <code title="post /profit">client.profit.<a href="./src/fv/resources/profit.py">calculate</a>() -> <a href="./src/fv/types/profit_calculate_response.py">ProfitCalculateResponse</a></code>

# Pack

Types:

```python
from fv.types import PackListResponse
```

Methods:

- <code title="get /pack">client.pack.<a href="./src/fv/resources/pack.py">list</a>() -> <a href="./src/fv/types/pack_list_response.py">PackListResponse</a></code>

# Me

## Card

Types:

```python
from fv.types.me import CardHireResponse, CardSellResponse
```

Methods:

- <code title="put /@me/card/{usercard_id}">client.me.card.<a href="./src/fv/resources/me/card.py">update</a>(usercard_id, \*\*<a href="src/fv/types/me/card_update_params.py">params</a>) -> None</code>
- <code title="post /@me/card/hire">client.me.card.<a href="./src/fv/resources/me/card.py">hire</a>(\*\*<a href="src/fv/types/me/card_hire_params.py">params</a>) -> <a href="./src/fv/types/me/card_hire_response.py">CardHireResponse</a></code>
- <code title="post /@me/card/sell">client.me.card.<a href="./src/fv/resources/me/card.py">sell</a>(\*\*<a href="src/fv/types/me/card_sell_params.py">params</a>) -> <a href="./src/fv/types/me/card_sell_response.py">CardSellResponse</a></code>
- <code title="patch /@me/card/{usercard_id}/captain">client.me.card.<a href="./src/fv/resources/me/card.py">set_captain</a>(usercard_id) -> None</code>

## Pack

Types:

```python
from fv.types.me import PackBuyResponse, PackOpenResponse
```

Methods:

- <code title="post /@me/pack/{pack_id}/buy">client.me.pack.<a href="./src/fv/resources/me/pack/pack.py">buy</a>(pack_id) -> <a href="./src/fv/types/me/pack_buy_response.py">PackBuyResponse</a></code>
- <code title="post /@me/pack/{pack_id}/open">client.me.pack.<a href="./src/fv/resources/me/pack/pack.py">open</a>(pack_id) -> <a href="./src/fv/types/me/pack_open_response.py">PackOpenResponse</a></code>

### Config

Types:

```python
from fv.types.me.pack import ConfigRetrieveResponse
```

Methods:

- <code title="get /@me/pack/config">client.me.pack.config.<a href="./src/fv/resources/me/pack/config.py">retrieve</a>() -> <a href="./src/fv/types/me/pack/config_retrieve_response.py">ConfigRetrieveResponse</a></code>
- <code title="put /@me/pack/config">client.me.pack.config.<a href="./src/fv/resources/me/pack/config.py">update</a>(\*\*<a href="src/fv/types/me/pack/config_update_params.py">params</a>) -> None</code>

# Redeem

Types:

```python
from fv.types import RedeemRedeemCodeResponse
```

Methods:

- <code title="post /redeem">client.redeem.<a href="./src/fv/resources/redeem.py">redeem_code</a>(\*\*<a href="src/fv/types/redeem_redeem_code_params.py">params</a>) -> <a href="./src/fv/types/redeem_redeem_code_response.py">RedeemRedeemCodeResponse</a></code>

# Lineup

Types:

```python
from fv.types import LineupSetConfigResponse
```

Methods:

- <code title="post /lineup/formation/{formation_id}">client.lineup.<a href="./src/fv/resources/lineup/lineup.py">set_config</a>(formation_id) -> <a href="./src/fv/types/lineup_set_config_response.py">LineupSetConfigResponse</a></code>

## Card

Methods:

- <code title="delete /lineup/card/{usercard_id}">client.lineup.card.<a href="./src/fv/resources/lineup/card.py">down</a>(usercard_id) -> None</code>
- <code title="post /lineup/card/{usercard_id}">client.lineup.card.<a href="./src/fv/resources/lineup/card.py">up</a>(usercard_id, \*\*<a href="src/fv/types/lineup/card_up_params.py">params</a>) -> None</code>

## Image

Methods:

- <code title="get /lineup/image">client.lineup.image.<a href="./src/fv/resources/lineup/image.py">get</a>() -> object</code>
- <code title="get /lineup/image/{user_id}">client.lineup.image.<a href="./src/fv/resources/lineup/image.py">get_by_user_id</a>(user_id) -> object</code>

# User

## Me

Types:

```python
from fv.types.user import User
```

Methods:

- <code title="get /user/@me">client.user.me.<a href="./src/fv/resources/user/me.py">retrieve</a>() -> <a href="./src/fv/types/user/user.py">User</a></code>
- <code title="patch /user/@me/language">client.user.me.<a href="./src/fv/resources/user/me.py">update_language</a>(\*\*<a href="src/fv/types/user/me_update_language_params.py">params</a>) -> <a href="./src/fv/types/user/user.py">User</a></code>

# Card

Methods:

- <code title="get /card/{card_id}/image">client.card.<a href="./src/fv/resources/card.py">retrieve_image</a>(card_id) -> None</code>

# Match

Types:

```python
from fv.types import MatchJoinRankedResponse
```

Methods:

- <code title="post /match/ranked">client.match.<a href="./src/fv/resources/match.py">join_ranked</a>() -> <a href="./src/fv/types/match_join_ranked_response.py">MatchJoinRankedResponse</a></code>

# Userinventory

Types:

```python
from fv.types import UserinventoryRedeemResponse
```

Methods:

- <code title="post /userinventory/redeem/{userinventory_id}">client.userinventory.<a href="./src/fv/resources/userinventory.py">redeem</a>(userinventory_id) -> <a href="./src/fv/types/userinventory_redeem_response.py">UserinventoryRedeemResponse</a></code>

# Auth

Types:

```python
from fv.types import AuthLoginDiscordResponse
```

Methods:

- <code title="post /auth/discord">client.auth.<a href="./src/fv/resources/auth.py">login_discord</a>(\*\*<a href="src/fv/types/auth_login_discord_params.py">params</a>) -> <a href="./src/fv/types/auth_login_discord_response.py">AuthLoginDiscordResponse</a></code>
