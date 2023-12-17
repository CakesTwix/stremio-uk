from schemas import Preview, Series, Videos

catalog_tv = [
    Preview(
        id="oneplusone",
        type="tv",
        name="1+1 Україна",
        genres=[],
        poster="https://farmak.ua/wp-content/uploads/2019/09/65cfb931070ae316bf98eeebda4e5f02_1245x450.png",
        description="ТВ шоу, фільми і серіали 1+1 медіа. Цікаві новини зі світу шоу бізнеса. Телепрограма на весь тиждень.",
    ),
    Preview(
        id="tet",
        type="tv",
        name="TET",
        genres=[],
        poster="https://ideil.com/static/uploads/Tl2XMc3oxLBSkXlwyE3ylH6d6TemmLH47ELIy7Ry.jpg",
        description="ТЕТ (Тонис Ентер Телевижн) — украинский развлекательный телеканал.",
    ),
]

meta_tv = {
    "oneplusone": Series(
        id="oneplusone",
        type="tv",
        name="1+1 Україна",
        description="ТВ шоу, фільми і серіали 1+1 медіа. Цікаві новини зі світу шоу бізнеса. Телепрограма на весь тиждень.",
        genres=[],
        director=[],
        background="https://farmak.ua/wp-content/uploads/2019/09/65cfb931070ae316bf98eeebda4e5f02_1245x450.png",
        videos=[
            Videos(
                id="oneplusone",
                title="Канал",
                thumbnail="https://cdc.ua/uploads/tv_service_channel/4/11_hd.png",
            )
        ],
    ),
    "tet": Series(
        id="tet",
        type="tv",
        name="TET",
        description="ТЕТ (Тонис Ентер Телевижн) — украинский развлекательный телеканал.",
        genres=[],
        director=[],
        background="https://ideil.com/static/uploads/Tl2XMc3oxLBSkXlwyE3ylH6d6TemmLH47ELIy7Ry.jpg",
        videos=[
            Videos(
                id="tet",
                title="Канал",
                thumbnail="https://mediananny.com/content/images_new/news/620x408/57673.jpg",
            )
        ],
    )
}
