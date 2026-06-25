import asyncio
from database import init_db, add_track
from parser import parse_playlist, auto_detect_genre

# ВСТАВЬ СЮДА СВОЙ СПИСОК ИЗ 1520 ТРЕКОВ
MY_PLAYLIST = """Каспийский Груз - В бараке
AVORA - Душа кайфуй
Артур Назаров, Голос Ермака - Над Донбассом
Гио Пика, Эндшпиль, МанТана - Х2
Andy Panda, Miyagi - Endorphin
SAYAN - Закрой мои глаза
Никита Лович - По гражданке
9 грамм - Ворон
Kenndog - Beethoven
Каспийский Груз - Режим построже
Draxxxy, Klubok - Star
Каспийский Груз - По ресторанам
Белка - Егермейстер
Artamonova - Direct
Miyagi & Эндшпиль - RudeBoys
onokami - ангелочек  (prod. staticplus)
Big Baby Tape - Chuchuka
Дора, Мэйби Бэйби - Дежавю
Брутто - Ирландец
Рем Дигга, NyBracho - Фонари
Молодой и Скромный - Молодой пацан
V $ X V PRiNCE - Цветы
Каспийский Груз - Красива 80lvl
ХАНЗА, OWEEK - Вечеринка
Эндшпиль - Моя мама
moulses, Alik Zargarov - Клеопатра (hoodtrap)
Каспийский Груз - Не выйдет
TRUEтень, Эндшпиль - На Чай
KADI, Miyagi - Prayers
Galezard Project - Spirits in the Night
MKHLSDRV - За горами, за желтыми долами
Al Rakhim, Medkova, Байоз - Капризная (remake)
SCIRENA - Мамин продакшн
Colorit - Ты одна
Mav-d, Miyagi & Эндшпиль - Мосты
Boni.ka - Или она или никто
16canva, MallBoy - my humor
KYANU, DJane HouseKat, Darius & Finlay - My Party
Эндшпиль, TumaniYO - WAKE UP
KADI, Miyagi - Colors
Big Baby Tape, BUSHIDO ZHO, Scally Milano - DRUNK
Ратный - Розовеет рассвет
Aarne, Toxi$, OG Buda - NaNaNa
NESVOY - Горы
ICEGERGERT - G-Woman
Miyagi & Эндшпиль, TumaniYO - Sample
Лоя - Я буду
Мэйби Бэйби, DEAD BLONDE - Beverly Hills
KEN TEE - Нужная Важная Милая
ERENWOODS - Покатаемся по городу
Анри - Вива Да Лока
onna badvibes, Эндшпиль - melt
Денис RiDer, SHAQINA - Бархат
Брутто - Action
Culture Beat - Crying in the Rain
Yaki-Da - Teaser on the Catwalk
Эд  Изместьев - Сильное чувство
Каспийский Груз, Влади - Герои нашего времени
ICEGERGERT - Amsterdam
Miyagi - Настырный
Don Padro, Vladosik_500 - Лям 200
ANIVAR - Украду
Мэйби Бэйби - Такая любовь
Намо Миниган, Miyagi & Эндшпиль - Море
ALIBAEV, Akonya - YMB
Adil - Госпожа
Konfuz - Ути путишка
HLOY, Эндшпиль - One smile
ARKUSHA - Чмок
V $ X V PRiNCE - День или ночь
Брутто - Однажды он
Miyagi - Runaway
Рем Дигга, Деловой - 1
LUCAVEROS - Накроет волной
RASA, kavabanga Depo kolibri - Фиолетово
OKSII, LKN - Невеста
ANIVAR - Лето
Soul - Adios
KA'MI - Рядом с тобой
Al Fakher - #Музыкадлядуши
Элджей - 360º
Магамет Дзыбов - Лалеби
Мэйби Бэйби - Феноменальна
Тайпан, Agunda - Луна не знает пути
Rakhim - Fendi
Konfuz - Пропал интерес
Miyagi, Эндшпиль - Нутро
Джарахов, Markul - Я в моменте
Брутто - Cadillac
RaiM, Artur, Adil - Симпа
Шалих - Солдат
Miyagi & Эндшпиль, Mav-d - Skittles
V $ X V PRiNCE, BOLLO - Пусто
WANTARAM - Сыны России
Тимур Танкист - Парни с шевронами
The Limba, HIRO - Интерес
Miyagi - Корабли
HLOY, Эндшпиль - Высота
Моя Мишель, ЛСП, DFM - Курточка
RADIO TAPOK - Петропавловск
BRANYA, MACAN - Пополам
Miyagi & Эндшпиль, TumaniYO - West
ARTIK & ASTI - Истеричка
MIA BOYKA - Черная LADA
SoLLo - Её фигура
Miyagi - Время
Castle, Эндшпиль - Control
I.L.A.Y., С.В.О.Й - Злой уральский самурай
Сергей Трофимов - Город Сочи
БРОСКО, ТАБИК - Ходит такой слушок
RADIO TAPOK - Битва за Москву
Miyagi & Andy Panda - Get Up
Boni.ka - Прямо в сердце
ПослеZавтра - Быть воином - жить вечно!
I.L.A.Y., С.В.О.Й - Дурочка война
Группа Брызги - Позывной Ромашка
Miyagi & Эндшпиль - Groove
Юлианна Караулова, ST - Море
SCIRENA - Деньги и Москва
MONA - Иордан
By Индия, Xcho, MOT - Шадэ
Асия - Мона Лиза
V $ X V PRiNCE - Точка или запятая
Эндшпиль - По пятам
Miyagi & Эндшпиль - Новый день
16canva - klubok
Ксения Юхнова - Письмо солдату
Nasty Babe - Гаснет свет
Намо Миниган, Miyagi & Эндшпиль - Воином
Рем Дигга - В огне
V $ X V PRiNCE - Мурашки
KRBK - Девушка в чёрном
Лолита - На Титанике
GaoDagamo, Nesvyat, Miyagi - На уверенном
Эндшпиль - Слоем дыма
Баста, GUF - Чайный пьяница 2.0
просто Даня - влюбился в казашку
RIPSI - Милая, засыпай
КИНО - Кончится лето
16canva - friends
Jakone, SCIRENA - Там Там
Катюша - Maybach
Дора, ТРАВМА - Трудный возраст
Макс Корж - Малиновый закат
RADIO TAPOK - Белая лилия
V $ X V PRiNCE - За ней
LazyShau, DronGo, Drongo - forest
Рем Дигга - Дикарь
Big Baby Tape - LOX
Miyagi & Andy Panda, TumaniYO - Оттепель
Эндшпиль, onna badvibes - Aura
Брутто - Суета
Каспийский Груз, HORUS, ATL - Ночь
Свойский - Made in Russia
ANIKV, SALUKI - Меня не будет
КИНО - Группа крови
Miyagi - Колибри
Баста - Урбан
JIMBEI - Аревуар
Jakone, A.V.G - Платина
rubchanskii - мокрая девочка
V $ X V PRiNCE - MAMA-MiA
HOMIE - Лето
Ксения Юхнова - Держитесь парни
Miyagi & Эндшпиль - Лабиринты
Miyagi & Эндшпиль, MAXIFAM - Без обид
Рем Дигга - Тюльпан
Ксения Юхнова - Там брат за брата
Эндшпиль, TumaniYO - It's My Life
Каспийский Груз, ВесЪ - Мани-мани
Miyagi - Дизлайк
Ксения Юхнова - Движение вперёд
ARTIK & ASTI - Номер 1
Рада Рай - Край родной (Туган як)
Miyagi & Эндшпиль - Дама
NANSI & SIDOROV, Женя Трофимов - Последний вальс
Люся Чеботина - Солнце Монако
Эндшпиль, МанТана, Гио Пика - Палево
Брутто - Молодой
RADIO TAPOK - Курская битва
Киньте Копеечку - Нива
wavdealer - Zerkalo
Каспийский Груз, Xpert - Афганистан
Катюша, MLDL, Parfenxv - Maybach 2.0
Алиса Буслова, 33Mb - СЕВЕР-ЮГ
Чародея, MURATOVSKY - Я по полю DANCE
BARSOVA - Родина Россия
Miyagi - Дом
Quest Pistols Show - Санта Лючия
HammAli & Navai - Пустите меня на танцпол
Бабек Мамедрзаев - Принцесса
Konfuz - Ратата
LUDOMUSIC - Учит казик
BREMEYER - Your Body My Body
Karna.val - Психушка
Азамат Биштов, Мурат Тхагалегов - Сердце
Miyagi & Эндшпиль, Truwer - No Reason
Miyagi - Ночи в одного
V $ X V PRiNCE, Tony Tonite - Карусель
Rauf & Faik - Я люблю тебя
Рем Дигга, L iZReaL - + 500
Каспийский Груз - Хамам
Miyagi & Эндшпиль, Drew - I Can Fly
ГУДЗОН - Влюбилась в пацана
Jakone, SCIRENA - По весне
GAYAZOV$ BROTHER$ - МАЛИНОВАЯ ЛАДА
ABIEM Project - Ой, по над Волгой
Брутто - День знаний
Баста, HammAli & Navai - Где ты теперь и с кем
PI1eER - Интрижка в лесу
RADIO TAPOK - Халхин - Гол
Miyagi, Ollane - Весна
A.V.G, Goro - Она близко
Каспийский Груз - Буду честен
Miyagi & Эндшпиль, Рем Дигга - Don't Cry
GAYAZOV$ BROTHER$ - Там, где кайф
Супер Жорик - Золото
RADIO TAPOK - Брестская крепость
VERBEE - Зацепила
Мурат Тхагалегов - Сердце
Василя Фаттахова - Туган як
MIA BOYKA - ЭКСПОНАТ
Miyagi & Эндшпиль - Bullet
Кэнни, МС Дымка - Ворона
Miyagi - По уши в тебя влюблён
Брутто - Бандит
TAF - Я солдат
Антон К. - За победу
Вахбет Абедов - Водка пиво
Vuska Zippo - Душа, кайфуй
Ксения Юхнова - Движение вперёд 2.0
Miyagi & Эндшпиль - Я хочу любить
opm. - Чёрные глаза
Шамиль Кашешов - Потому что я влюблён
СТРОГИЙ, Skyth27 - Русский солдат
Олег Бодров - Здравствуй, Мама
Ислам Итляшев - Мирный, красивый край
Саграда, Соль земли - Давай за...
Каспийский Груз, Сергей Трофимов - Ночевал
Баста, GUF - Только сегодня
Амур Успаев - Да, да, да - это Кавказ
Студия "Офицеры России" - Вам Русских!... Никогда не победить!
Альберт Назранов - Сердце
Monoir, Arabella - Dubai
ALEX DJ, Dr.Nap - Bailando 2013
Заур Магомадов - Курильщикам трудно / Караван
Каспийский Груз - Любовь HD1080
Каспийский Груз - Адик Original
Джама, Jaspa Vol, Chesta - Звуки урбана
V $ X V PRiNCE - Jamaika
Любэ, Санчес, Yopt - Солдат
Ратный - БПЛА
SAYAN - Мальборо
Miyagi & Эндшпиль - Obrigado
Primo Block - Я ВЕРНУСЬ
Miyagi & Эндшпиль, KREC - Нирвана
Rauf & Faik - Детство
АрЧи - Русский штурмовик
MilitaryHub, TAMIK - Не Герой
Каспер - Завтра повезëт
Акафист - Вагнер
R.P.G. - Братство музыкантов
boneyblaze - ДУША ПОЭТА
I.L.A.Y., С.В.О.Й, ROMAN 7.62, МК 5.45 - Вернёмся домой
Эндшпиль - С неба
nicebeatzprod., Badda Boo - улетаю (feat. Badda Boo)
Ратный - БПЛА (Акустика)
Олег Бодров - Падали
LOVELYDILLER - Малышка ревнует
ЛСП - Бейби
GUF - Письмо домой
WallClan - Пьяные танцы
ASYAMF - Уходил
9 грамм - Ла ла лэй
wyloune - температура
Miyagi & Эндшпиль - God Bless
ati2x06, oclody, OVERDOSEFLEX - Спать с тобой
Mr.NЁMA, гр. Домбай, MriD - Лада Приора
foxypuma - Мальчик не рыдай
Andery Toronto, Криминальный бит, MIROLYBOVA - Умница
T1One, Inur - Почему так больно
Мой двор - Здравствуй, мама
Miyagi & Эндшпиль - Наоборот
Damaji - Дай мне надежду
ОПЯТЬ - Не итальянцы
САМЕДЛИ - Ты такая по приколу
ЛЯЛЬКА - Трахаца
Готлиб, SATS - У ДЕТКА
Deesmi, Onlife - Влюбился в неё
Seeped, Seeped, Speedy Audio, Speedy Audio - SND
Перфе - Не верю
Daybe - На часах нули
moulses - Принцесса (hoodtrap)
10AGE, ХАНЗА - Пишешь мне пока
KOREL - Кис-кис
The Limba - Обманула
TERRY - Домофон
Dino MC47 - Никто не забыт
QKooK, TAMIK - 149.200
Тимати, ЕГОР КРИД - Гучи
Diazz - Вся моя
V $ X V PRiNCE - На лету
seneamin - Москва - Татарстан
Isko - Любовь в ресторане
Andery Toronto, Диман Брюханов - Решето
Dobryi - Настоящая любовь
TAMIK, QKooK - Доброволец
Самсон Богородский, Марк Яровный - Доктор
Эндшпиль, ТАТО - НА СТОРОНКЕ
TAMIK, Andy - Лилии
Moreart - Tom Ford
GUF, A.V.G - Спонсор твоих проблем
ENTYPE - не нужна
Элджей, Era Istrefi - Sayonara детка
9 грамм - Секс
Saga - Детка, играй
Эндшпиль, Ollane - Приятная
Miyagi & Эндшпиль - Не теряя
Рем Дигга - Далеко
Kempel - Я так хочу
Mr Lambo - Jackpot
Santiz - Кайфуша
Витя АК - Апокалипсис
KLLIN - Голливуд
Вектор А - Лирика
Макс Корж - Пьяный дождь
Жаман, John - О глубоком
10AGE, Ramil' - Ау
Miko - Девочка в тренде
Триагрутрика - Биг сити лайф
SVNV, BULA - Тлеет
Элджей - Минимал
RYZE - Тебя манят
moulses - Глаза карие (hoodtrap)
Брутто - Кинотеатр «Дружба»
THRILL PILL, ЕГОР КРИД - Грустная Песня
notscale, ErickoSimans, goatzilla - Ты Говорила 2 (Каждый Раз Remix)
Ирина Кайратовна, Junior - Ne Áńgime?
TEKSIDR - Хэппи энд
KOREL, NEEL - Она делит вайб
Right Person - Кофта пахнет твоим домом
GUMA - Стеклянная
IBIZA01 - Положение
Кот Балу, Каспийский Груз - туда и обратно
mizlzim - Ничего личного
mizlzim, LADYVERONIKA - Фиеста
mizlzim, LADYVERONIKA - Фиеста (Speed Up)
mizlzim - Я закрыла двери
Konfuz - Кайф ты поймала
Miyagi - Sorry
HammAli & Navai - Девочка-война
Ulukmanapo - Denzel W.
Miyagi & Эндшпиль, Brick Bazuka - Бошка
V $ X V PRiNCE - Суета
Лёша Свик - Малиновый свет
KURT GUETTO, TRAKOV - Uno dos tres
IVAN VALEEV - Novella
Смоки Мо, GUF, Dj Cave, Lil Kate - Станция
DIOR, samo - Положение
DAKOOKA - Умри, если меня не любишь
DAKOOKA, ШГШ - не переживай
ЛИТВИН - Жы Ши
миндаль - ПОКАЖИ АЙ
Eiffel 65, Luis Rodriguez - Too Much Of Heaven Luis Rodriguez Remix
badCurt - Миллион чувств
Big Baby Tape - Like A G6
Смоки Мо - До утра
ПИЧМАСТЕР, креатор, нимфа - пубертат
Ирина Кайратовна - 5000
Мэйби Бэйби, Baby Cute, Дора - Вуаля
Элджей - Рваные джинсы
ЕГОР КРИД, Tenderlybae, Шкред - Таро
ТихоДумал - Мне похуй я в России
Ghetto Dogs - Tateler
Miyagi & Эндшпиль, Рем Дигга - Untouchable
Torviro - NO LIE
ЛСП - Холостяк
COLDCLOUD - LUV 2
Скриптонит, Charusha - Космос
The Limba - Обманула
Miyagi & Эндшпиль - Временно
V $ X V PRiNCE - Далада
V $ X V PRiNCE - Солнце (prod. by Klein & Rigas)
ЛСП - Холостяк
Мэйби Бэйби - Лаллипап
Пошлая Молли - Нон стоп
Город 312 - Останусь
V $ X V PRiNCE, GUF - До-Ма
Мэйби Бэйби - BABYBARS
DJ WaWa - Я тебя не отпущу.
Hi-Fi - Не дано
LOVV66 - МАЙ МАЙ
TumaniYO, Miyagi & Эндшпиль - Dance Up
REFLEX - Потому что не было тебя
moulses - Бродяга
Roza Filberg - В белом самолете
Валерия - Маленький самолёт
Полка - Чем прежде
9 грамм - Дэнс
Рем Дигга - На юг
Baby Gang - Mentalité
Big Baby Tape - Surname
mizlzim - Три минуты - это норма
Miyagi & Эндшпиль - Hajime
лучнадежды - Мимолетно
АК-47 - Але, это Пакистан
GUF, BALLER, V $ X V PRiNCE - ШАРАУТ
H8.HOOD - Жмурки
Тимати, ЕГОР КРИД - Где ты, где я
Гио Пика - Xpоникa-Бeлoмopкaнaл
Эндшпиль - Атаман
Мэйби Бэйби - Барби из трущоб
Draxxxy - TERRORIST
Draxxxy - RICH
Каспийский Груз, Mania - Давай уедем
МК 5.45 - Русские идут (ВИТЯЗИ)
Тимур Танкист - Для врага я Русский
Каспийский Груз - Осторожно Окрашено
Каспийский Груз - Табор вернулся в город
Каспийский Груз, Гансэлло - Сам всё знаю
С-КОРПУС - Мы - русская честь
Гио Пика - Едет-катится
Ставр - В этих окопах нет атеистов
Miyagi & Эндшпиль - Двигайся
Каспийский Груз - Преступник
Акафист - Музыкант
Рем Дигга - Универсальный солджа
MilitaryHub - Посадки
Draxxxy - PAST LIFE
INNA - Sun Is Up
Maroon 5, Christina Aguilera - Moves Like Jagger
Big Baby Tape - Hokage
Jennifer Lopez, Pitbull - On The Floor
Гости из будущего - Он чужой
speed up & nightcore, slowed & slowcore - easy-to-reach girl
Гио Пика - Xpоникa штрафбат
The Flashers Brothers - Stereo Love
Maria Levinson, Nick G, Mia Love, Nic Perez - Rockabye
MIA BOYKA, Московский Казачий Хор - Богатырская
DEAD BLONDE - Всего лишь друг
Mustafa Sandal - Araba 2004
Валерия - Капелька
КИНО - Пачка сигарет
Моя Мишель, ЛСП - Курточка
GONE.Fludd - BARBIE
Sting - Shape Of My Heart
Земфира - лампочки
Miyagi & Andy Panda - Буревестник
УННВ - Муза
Jennifer Lopez, Pitbull - On The Floor
zhanulka - ток
zhanulka - портреты
zhanulka - кискис
Junior - ВАТ ИЗ ЛАВ
Руки Вверх! - Думала
moulses - Дыши (hoodtrap)
moulses - Свела с ума (hoodtrap)
moulses - Чародейка (hoodtrap)
UncleFlexxx - SMS
HOLLYFLAME - Тону
Василииса - Ойся, ты ойся
Imagine Dragons - Bones
ЛСП - Шиншиллы
Jakone, Kiliana - Жиганская
ICEGERGERT, Zivert - БАНК
SQWOZ BAB - КУПЕР
Гости из будущего - Беги от меня
NikitA - Машина
ЯКОРЪ, НАВЕРНОЕ ПОЭТ - #ЛЯШКИВКУСНЯШКИ
Валерия - Капелькою
Selena Gomez & the Scene - Love You Like A Love Song
МакSим - Ветром стать
Peggy Gou - (It Goes Like) Nanana
Alexandra Stan - Mr. Saxobeat
Город 312 - Фонари
Лоя - Малышка (Я буду)
Вирус, MVGMA - Не ищи
Gabry Ponte, Erika - I Don't Know
Планка - На грани болевого порога
ARTIK & ASTI - Неделимы
КАЗАКИ ДЕЛАЮТ ХИТЫ - Облака
Lx24 - Танцы под луной
Mav-d, Miyagi & Andy Panda - Темнота
Андрей Губин - Облака
Руки Вверх! - Танцуй
Валерия - Часики
MARSTEREON, Polly Belycee, Deep Mage - Rockabye
Эндшпиль, Ollane - Mi Amor
Оксана Почепа (Акула) - Позвони
R.P.G. - OSW
Jennifer Lopez - On The Floor
Руки Вверх! - Чужие губы
Краски - Он Не Знает Ничего
NYUSHA - Выбирать чудо
IOWA - Мои стихи, твоя гитара
kizaru - Зеркало
SEREBRO - Я тебя не отдам
нежность на бумаге - Песенка прокрастинатора
R.P.G. - Белые дяди
Рок-острова - Ничего не говори
ФОГЕЛЬ - БОГАТЫМИ
Miyagi & Эндшпиль, TumaniYO - Fuck the Money
Дискотека Авария, Жанна Фриске - Малинки-Mалинки
Краски - Оранжевое Солнце
Джиган, Тимати, ЕГОР КРИД - Rolls Royce
Jakone, A.V.G, Итачи - Курить
GSPD, DEAD BLONDE - У России три пути
DEAD BLONDE - Мальчик на девятке
Руки Вверх! - Выпускной
АЙВЕНГО, Варя Бутко, Хор "Достояние республики", Российское движение школьников, Юнармия, Большая перемена - Родина Россия
R.P.G. - Звёзды за 500
xxxmanera - Never Broke Again
N1NT3ND0 - ЧП
kizaru - Money long
Big Baby Tape - Gimme The Loot
Miyagi & Эндшпиль, KADI - In Love
Fisun, Niki Four - Only You
Диана Гурцкая - Нежная
Nasty Babe - Патрики
DONI, Сати Казанова - Я украду
Big Baby Tape, kizaru - Ride Or Die
Дима Билан - Я твой номер один
Демо - Солнышко 2013
Татьяна Буланова - Ясный мой свет
Big Baby Tape, kizaru - 99 Problems
Эндшпиль - My Babylon
Валерия - Обо мне вспоминай
МакSим - Сон
DJ DimixeR, Dmitrii G, ЧЕРРИ, Александр Порфирьевич Бородин - Улетай
Каспийский Груз, L iZReaL - Детство
МакSим - Не отдам
Антиреспект - Тишина
Бутырка - Запахло весной
Алёна Апина - Бухгалтер
Miyagi & Andy Panda - Atlant
Пошлая Молли - Контракт
Жанна Фриске - Ла-ла-ла
Руки Вверх! - Он тебя целует
DEAD BLONDE - Питер – город криминала
Монеточка - Ириски и риски
SEREBRO - СЛАДКО
Miyagi & Эндшпиль - Listen to Your Heart
Каспийский Груз - Сарума
Виктор Цой - Группа крови
Оксана Почепа (Акула) - Мало
KaYL - Lipsi Long
daryana - хейтер
Натали - Ветер с моря дул
Мэйби Бэйби - Бла Бла
5sta Family - Снова вместе
La Banda del Diablo - Danza Kuduro
Miyagi & Andy Panda - Medicine
Екатерина Яшникова - Я останусь одна
Юлианна Караулова - Внеорбитные
Дима Билан, МакSим - Знаешь ли ты
Артур Пирожков - #Алкоголичка
Чай вдвоём, Стас Костюшкин, Денис Клявер - День рождения
JekaMit - Россия наступает
Жанна Фриске - А на море белый песок
Андрей Губин - Девушки как звёзды
Стас Михайлов - Всё для тебя
Miyagi - Texture
Бутырка - Аттестат
R.P.G. - Столица
Эндшпиль - Джанго
Руки Вверх!, ASTERO - Когда мы были молодыми
Сява - Меня вставляет ритм
ESTRADARADA - Вите надо выйти
SEREBRO - Отпусти меня
Aarne, Toxi$ - KM
Miyagi & Эндшпиль - Бейба судьба
Lynaro - FRIDAY
Big Baby Tape, kizaru - Million
AceMitchh - Confess your love (hoodtrap)
DJ Asul - MATADORA
ZXKAI - NO BATIDAO
Steel Deluxe, Катя Самбука - Сказка
Катя Лель - Муси-пуси
Игнатий Винтуров - Тело - убийца
LOBODA - случайная
ХАННА - Потеряла голову
Mr.NЁMA, Группа «Домбай» - Приора
МакSим - Отпускаю
SEREBRO - Сломана
LUCAVEROS - Дома
Big Baby Tape - LIT
vibermx - MONTAGEM NO BATIDAO - Slowed
Натали, MC DONI, DONI - Ты такой
Звери - До скорой встречи!
Антиреспект - Тишины хочу
I.L.A.Y. - Без срока давности
Виктор Цой - Восьмиклассница
Эльбрус Джанмирзоев - Глаза твои карие (Глаза карие)
Фати Царикаева, Альбина Царикаева - Бадола
Диман Брюханов - БПАН
PIZZA - Фары
Каста, Крёстная семья - Номерок (feat Крестная Семья)
Это Радио - На мурмулях
Miyagi, TumaniYO, KADI - Bismarck
Тимур Танкист - 4 пацана
Митя Фомин - Все будет хорошо
4К - Милиция
Натали - О боже, какой мужчина
Клим Кривоносенко - О той весне
Блестящие - А я всё летала
ПослеZавтра - Русские придут
Chopper beatz. - Мне так не хватает твоей красоты
Винтаж, Red Max - Роман
Василииса - Улетай на крыльях ветра
Вера Брежнева - Любовь спасёт мир
Тимур Танкист - Послание
Глюк'oZa - Невеста
Халиф Атуев - Ва Марьяна
Adecvat_Production - За цвет голубых очей
BADGRUB, Оксана Почепа (Акула) - Слёзы (Акула Remix)
Maco Mamuko - Whiskey, cola & tequila
Тимати - Понты
SILVIA - Chevrolet Tahoe
Бутырка - А для вас я никто
Виктор Салтыков - Белая ночь
Тахмина Умалатова - Твоя любовь манила
IOWA - Плохо танцевать
Гио Пика - Ад-Колыма
Xcho, MOT - Баллада
Макс Корж - Армия
5sta Family - Вместе мы
БумеR - Не плачь
КИНО - Перемен
Руки Вверх! - Он тебя целует
Радмир Текеев - Не женюсь
ARTIK & ASTI, Артём Качер - Грустный дэнс
Каспийский Груз, Типси Тип - Как в советском кино
Ирина Салтыкова - Голубые глазки
LOBODA - к черту любовь
Big Baby Tape, kizaru - Bandana
Смоки Мо, GUF - Ненависть
VVS Cartel - MUEVELOU
SEREBRO - Мало тебя
INNA, Miss Kailly - Caliente
Звери - До скорой встречи!
Даня Милохин, Николай Басков - Дико тусим
IOWA - Бьёт бит
Руки Вверх! - Ай-яй-яй
SABINA - Дагестан
Моя Мишель, Dose - Пташка
Потап и Настя - Умамы
ВИА ГРА, Вахтанг - У меня появился другой
Михаил Круг - Владимирский централ
Блестящие, Жанна Фриске - А на море белый песок
КИНО - Звезда по имени Солнце
moulses - Бродяга (hoodtrap)
Каспийский Груз - Город невест
БАНД'ЭРОС - Манхэттен
Blue Affair, Sasha Dith, Carlprit - Я одна
Ёлка - Около тебя
Глюк'oZa - Снег идет
Андрей Катиков - Кустурица
The Limba - Секрет
Гио Пика - Фонтанчик с дельфином
Miyagi & Эндшпиль - When I Win
Каспийский Груз, MIRAVI - Голос
Mary Gu - Если в сердце живёт любовь
Глюк'oZa - Глюк’oza Nostra
Ёлка - Не брошу на полпути
Игорёк - My Love Танюха
moulses - Мелодия дождя (hoodtrap)
Король и Шут - Ведьма и осёл
Король и Шут - Прыгну со скалы
Король и Шут - Дурак и молния
Король и Шут - Лесник
Лолита - Шпилька-каблучок
Любэ - Ты неси меня река (Краса)
нексюша - На твиче
Гио Пика - Буйно голова 5
uniqe, nkeeei, ARTEM SHILOVETS - ТОЛПЫ КРИЧАТ
TATISIZE, PASHASNICKERS - TATI
NYUSHA - Выше
Ласковый май - Седая ночь
SOSKA 69 - БАСЫ ДОЛБЯТ
Gala, Molella, Phil Jay - Freed From Desire
shadowraze - showdown
xxxmanera - Скажи мне кто ты
Отпетые мошенники - Девушки (Девушки бывают разные)
Big Baby Tape - 4x4
MVRSXX, Kuznetsky Squad - ВЫЛЕТАЮ ИЗ ТАКСИ (КЛУБНИКА)
SOLIDNAYA - Как любовь
SAKXRA, Валерия - Часики
whisperingsong - THE LOST SOUL X FLOKI
Liza Evans - Ревную (Original version)
SABINA, Timaro - Dagestan
ВИА ГРА - Попытка № 5
МакSим - Трудный возраст
Оксана Почепа (Акула) - Слёзы на морозе
Винтаж, Red Max - Ева
Светлана Разина - Музыка нас связала
Света - Ты не мой
Академический Ансамбль песни и пляски Российской Армии имени А.В. Александрова - Смуглянка
Don Lore V - Danza Kuduro
Ёлка - Мальчик-красавчик
Руки Вверх! - Когда мы были молодыми
Big Baby Tape, Aarne - HOODAK MP3
Гио Пика - Буйно голова
Любэ - Солдат
LOBODA - К чёрту любовь
Восточный округ, John - Давай со мной за звёздами
Эльбрус Джанмирзоев - Весенний снегопад
Aarne, BUSHIDO ZHO - ВМЕСТЕ
Анна Герман, Вокальный квартет «Улыбка», Инструментальный ансамбль «Мелодия», Матвей Исаакович Блантер - Катюша
Рем Дигга - Тринадцатый
КИНО - Кукушка
CREAM SODA, Red Max - Никаких Больше Вечеринок
daryana - кто ты (original)
Dogewell - Вишнёвая семёрка
Слава - Одиночество-сука
Ласковый май - Розовый вечер
Сектор Газа - Бомж
Эльбрус Джанмирзоев - Дыши
Эльбрус Джанмирзоев - Чародейка
Эльбрус Джанмирзоев - Мелодия дождя
Эльбрус Джанмирзоев, Alexandros Tsopozidis - Бродяга
LOBODA - Твои глаза
Юрий Шатунов - Седая ночь
GAYAZOV$ BROTHER$ - Увезите меня на Дип-хаус
Баста, Алёна Омаргалиева - Я поднимаюсь над землёй
Виктор Цой - Звезда по имени Солнце
Сектор Газа - Лирика
Михаил Круг - Фраер
ARTIK & ASTI - Девочка, танцуй
R.P.G. - В стиле WG
#2Маши - Мама, я танцую
Ollane, Miyagi & Andy Panda - Where Are You
Духовность - Русь молодая
ЕГОР КРИД - Девочка с картинки
Дима Билан - Молния
Кравц, Гио Пика - Где прошла ты
Руки Вверх! - 18 мне уже
Игорь Скляр - Комарово
Zivert - Life
Серёга - Чёрный бумер
Ласковый май - Белые розы
DEAD BLONDE - Бесприданница
Любэ - Конь
Виктор Цой - Группа крови
A.V.G - Я плачу
Баста - Я найду тебя через века
Miyagi & Эндшпиль - Bounty
Адлер Коцба, Timran - Запах моей женщины
Xcho - Вороны
Евгения Сотникова - Улетай на крыльях ветра
Влад Порфиров - Ой, мама, не женюсь
Артур Пирожков - Зацепила
Король и Шут - Кукла колдуна
Konfuz - Италия
RSAC - NBA
Хор многодетных семей города Москвы - Дружная семья
QKooK, Анастасия Гуня - Против стаи
Иванушки International - Тополиный пух
Мужской хор «Русский формат» - Мы русские – с нами Бог!
Татьяна Овсиенко - Музыка нас связала
КУЧЕР, JANAGA - По щекам слёзы
Ирина Аллегрова - Младший лейтенант
XOLIDAYBOY - Пожары
Hi-Fi - Не верь слезам
Славик Хитов, Тембот Беданоков - Суета
Леприконсы - Хали-гали, паратрупер
Grivina - Я хочу
Жуки - Батарейка
Надежда Кадышева, Золотое кольцо - Широка река
Градусы - Голая
MBAND - Она вернётся
Dabro - На часах ноль-ноль
Полина Гагарина - Кукушка
Karna.val - ЧАСТУШКА
#2Маши - Босая
Дима Билан - Держи
Jakone, Kiliana - Асфальт
Юлия Савичева - Если в сердце живёт любовь
Андрей Губин - Ночь
Ваня Дмитриенко, Аня Пересильд - Силуэт
Ирина Дубцова - Люби меня долго
Zvonkiy - Голоса
CREAM SODA - Никаких больше вечеринок
BUSHIDO ZHO, Scally Milano, Полка - днями и ночами
Гио Пика - Отечество казённое
EVEN CUTE, ЯКОРЪ, НАВЕРНОЕ ПОЭТ, derzko69 - Welcome to Moscow
DEAD BLONDE - Банкомат
whyspurky, whylovly - Какая?
Света - Может да, может нет
Greatha Laurion - Whiskey Cola
Lyamev - leto solnce zhara
The Hit Crew - Around the World (La, La, La)
Trivane - WORTH IT
Carlito Flores - Macarena
Swanky Tunes - Летели облака
Ray Charles - Hit the Road Jack
Sean Paul, Dua Lipa, Sam Feldt - No Lie
Cover Masters - Coco Jambo
Major Lazer, DJ Snake, MØ - Lean On
Антон Беляев - Лететь
Nyvoria - CHEAP THRILLS
Crystal Waters - Gypsy Woman (La Da Dee La Da Da)
Kyra - Waka Waka (This Time for Africa)
Группа Мой Двор - Здравствуй, мама
I've Got The Moves! - Moves Like Jagger
Luis Fonsi, Mauricio Rengifo, Andrés Torres - Despacito
Те100стерон - Это не девочка
Pharrell Williams - Happy
SEREBRO - Мама Люба
МакSим - Знаешь ли ты
Каста - Вокруг шум
Ed Sheeran, Stormzy - Shape of You
Руки Вверх! - Крошка моя
Dj Chechen - Чеченская Лезгинка
The Cat Empire - The Lost Song
Агас - Азия - Евразия
Маша Мирова - Пустоцвет
Аида Ведищева - Песенка о медведях
Отпетые мошенники - Люби меня, люби
Катя Лель - Мой мармеладный
Абрикоса - Завтра выпускной
kochneva - обещай
Любэ - Ты неси меня река
Сергей Лазарев - Это всё она
ЕГОР КРИД, MOLLY - Если ты меня не любишь
Пара Нормальных - Вставай
Quest Pistols Show - Ты так красива
Интонация - Пускай
Lucenzo, Don Omar - Danza Kuduro
Конец фильма - Юность в сапогах
Miyagi & Эндшпиль - OneLove
VAVAN - Зацени
Кай Гетц, Pavel Kuzmin - Лицейский батл (OST «Пророк. История Александра Пушкина»)
Баста - Выпускной (Медлячок)
СТРЕЛКИН - Знай их поименно: Беслан
Yopt - Пацаны из ГРУ
BRATEEVSKY, Skyth27 - WAGNER
ФОГЕЛЬ - ВЫПУСКНИК
две тысячи ярдов - верните в моду любовь
Jah Khalib - Медина
С-КОРПУС - Русский фанат
Ваня Дмитриенко - Шёлк
MOT - День и Ночь
FEDUK, Баста, Моя Мишель - Хлопья летят наверх
Тима Белорусских - Окей
Lizer - Пачка сигарет
GUF - Ice Baby
Velmin - SUGARCRASH
АКУЛИЧ, Молодой Платон - ПОДАРОК
Юра Борисов, шварц - Поэт и царь (OST «Пророк. История Александра Пушкина»)
VAD BOYZ - MUEVELOU
Precipitation - Soldat
1NZZiDENT - i don't know (hoodtrap)
Гио Пика - Хроника-Беслан
Ixonara - IF WE EVER BROKE UP
ФОГЕЛЬ - ДУРАКАМ ВЕЗЁТ
losttales111 - посмотри на этого монстра
Aarne, BUSHIDO ZHO - SOS
daryana, NEXTIME - мдк
Айшат Айсаева - Северный Кавказ
Miyagi & Эндшпиль, NERAK - Именно та
Русский строй - Родина
nyan.mp3 - У батарей
MAKARELYA - Время
Лэйна - Малай на белом барсе
Асия - Ну чё ты такой хороший?
Ver$ace - NATURALENO
!nnoluvv - Пошлая Блондинка
Оля Шевченко - Снова в отряд
Минаева - Шоколадка
Монеточка - Кис Кис Кис
ЧЕЛОВЕК ЯЙЦА - ЗАЛЕТАРИКИ
LonelyStash, Готлиб - На стол
Баста - Моя Вселенная
kavabanga Depo kolibri - Колибри
NEXTIME - СВЕТЛАНА!
Lizer - Между нами
L'One, Варвара Визбор - Якутяночка
Эндшпиль, HLOY, Mav-d - Сон
daryana - juice
uniqe, nkeeei, ARTEM SHILOVETS, xxxmanera - АФТЕРПАТИ  (prod. by Wipo & Mikita)
Napylniik - 2 лимузина
ЯКОРЪ, НАВЕРНОЕ ПОЭТ, EVEN CUTE, Ernest Merkel - Я ЛЮБЛЮ БАСЫ
Каспийский Груз, Rigos, SLIMUS - 18+
Aarne, Toxi$, Big Baby Tape - NOBODY
Miyagi & Andy Panda - Tantra
De Kölsche Jecken - Sieben Tage lang (Was wollen wir trinken)
ATLXS - PASSO BEM SOLTO
ZXKAI, SLXUGHTER - NO BATIDAO (Ultra Slowed)
ФОНК, pHonk, РУССКИЙ ФОНК, БРАЗИЛЬСКИЙ ФОНК, Brazilian Phonk, Фонк Фонк Фонк! - ТикТок Дрифт Понесло
Каспер - Рассвет
Nodahsa - Я никогда не стану феминисткой
RADIO TAPOK - Сталинград
RADIO TAPOK - Танк Алёша
FEDUK - Моряк
FEDUK - Хлопья летят наверх
Taylor Swift - Shake It Off
Мэйби Бэйби - sH1pu4Ka!
Элджей, Кравц - Дисконнект
Асия, Аня Pokrov - Любовь с картинки
Мэйби Бэйби - Ахегао
Miyagi & Эндшпиль - Голгофа
ЕГОР КРИД - Мне нравится
алёна швец. - вредина
алёна швец. - //соперница//
Абрикоса - Август
КруЭлла - Тампоны!
Miyagi & Эндшпиль - Река
Miyagi & Эндшпиль - Ночь
Керсари - Советский Союз
ANNA ASTI - Царица
Монеточка - Папина любовница
Юлианна Караулова - Ты не такой
TATISIZE, PASHASNICKERS - NPC
ToneMira - ангелы не спят
Aarne, BUSHIDO ZHO - DRAIN SEASON
Miyagi & Andy Panda - Психопатия
Miyagi & Andy Panda - All the Time
Монеточка - Селфхарм
Бамбинтон - Зая
Sayfalse, cape, JXNDRO - Montagem Rugada
dabbackwood - не попался
Sabi, MIA BOYKA - Базовый минимум
Артём Кальянов - Терриконы
Slowyver - SAFE AND SOUND
SKLЯR Алексей Скляренко - Про 90-ые
SKLЯR Алексей Скляренко - Чем взрослые отличаются от детей
Мэйби Бэйби - ЗАЙКА
Катя Самбука - Пати
whyspurky, whylovly - Какая? (Speed Up)
Vifitof - CALL ME MAYBE
Miyagi & Эндшпиль - Last of us
Екатерина Яшникова - Это возможно
SOSKA 69 - Чёрная машина
Miyagi & Эндшпиль - Круговорот
Эндшпиль - Я подарю
паранойя - ALASKA PUFFER
Михей и Джуманджи - Сука Любовь
T-Fest - Улети
Kim Petras - XXX
Miyagi & Andy Panda - Yamakasi
5sta Family - Я буду
AKORGO BOYS - ДЫК КЫН ДЫШ
SuperZloy - Теория безумия
Екатерина Яшникова - Песня о себе
Каспийский Груз - Доедешь — пиши
Miyagi - Самурай
Alphaville - Forever Young
The Hatters - Мечта
The Hatters - Да, со мной не просто
Моя Мишель - Зима в сердце
Miyagi & Эндшпиль - Silhouette
zhanulka - наколки
Стас Море, Аня Клюква - На моря
bridge - ЛАБУБА
bridge, treit - ЛАБУБА
Ленинград - Экспонат
Мэйби Бэйби - BABYBARS 3
Miyagi & Эндшпиль - Look at the Scars
Jason Derulo, Snoop Dogg - Wiggle
Consoul Trainin, Steven Aderinto, DuoViolins - Obsession
Carly Rae Jepsen - Call Me Maybe
Звери - Районы-кварталы
Надежда Кадышева - Плывёт веночек
Бьянка - А чё чё
ЕГОР КРИД - Будильник
Miyagi & Эндшпиль - Колизей
Miyagi & Эндшпиль - Фая
itgmq Brazil, DXWNFAME - попа как у ким
Heronwater, BUSHIDO ZHO - Дай мне посмотреть
алёна швец. - Молекулярная физика
ALIZADE, Big Baby Tape - Gucci
КлоуКома - Кто такой?
Артур Пирожков - Чика
Sean Paul, Dua Lipa - No Lie
Ёлка - Всё зависит от нас
Дискотека Авария - Недетское время
Quest Pistols Show - Непохожие
МУККА - Девочка с каре
Miyagi & Эндшпиль, Sимптом - Люби меня
Miyagi & Эндшпиль - Фея
MC Zali - Джована
GAZIROVKA - Black
Ka-Re - Половина
30.02 - Звёзды в лужах
Те100стерон - Это не женщина
Алексей Воробьёв - Я тебя люблю
Miyagi - Angel
ЕГОР КРИД - Сердцеедка
zhanulka - ты похож на кота
кис-кис - Мальчик
COMEDOZ - Тётя Зина
COMEDOZ - Гимн дружбы Артека
Ver$ace, Ernest Merkel - NATUREMAN
SODA LUV - ЯЛРС (prod. by YG Woods, 8keey)
Смоки Мо, Miyagi - МОНБЛАН
ЕГОР КРИД - Папина дочка
ЕГОР КРИД, Филипп Киркоров - Цвет настроения черный
ЕГОР КРИД, NYUSHA - Mr. & Mrs. Smith
ЕГОР КРИД - Невеста
Бьянка - Были танцы
Сати Казанова, Arsenium - До рассвета
Мэйби Бэйби - Аскорбинка 2.0
Мэйби Бэйби - Аскорбинка
Мэйби Бэйби - Кардиограмма
Вера Брежнева - Близкие люди
Quest Pistols Show, Open Kids - Круче всех
Джаро & Ханза - Ты мой кайф
Miyagi & Эндшпиль, Miyagi, Эндшпиль, Al I Bo, Wooshendoo - #Тамада
Miyagi & Andy Panda, TumaniYO - Brooklyn
ЕГОР КРИД - Самая самая
PIZZA - Романс
Джаро & Ханза - Королева танцпола
RASA - ПОГУДИМ
S.I.K PRODUCTION - Лайтово
Miyagi & Andy Panda - Freeman
Manu Chao - Me Gustas Tú
RASA - Под фонарём
Capital Cities, Sebu Simonian, Ryan Merchant - Safe And Sound
Грибы, Sимптом - Тает лёд
Vance Joy - Riptide
Градусы - Режиссер
Ёлка - Грею счастье
Леонид Агутин, DJ DANI WOO - Остров
IOWA, Veshard - 140 (Dj Veshard Remix)
IOWA - Простая песня
PIZZA - Лифт
uniqe, nkeeei, ARTEM SHILOVETS, SAGARA - Лифон
Nikitata - ПОЛЮБИ МЕНЯ СИЛЬНЕЙ
Miyagi & Эндшпиль - Путеводная
BUSHIDO ZHO - vodila
The Limba, ANDRO - X.O
Монеточка - Каждый раз
JAWNY - Honeypie
Винтаж, ТРАВМА, SKIDRI, DVRKLXGHT - Плохая девочка
GONE.Fludd - КУБИК ЛЬДА
Miyagi, Mav-d, Ollane - Music is love
uniqe, nkeeei, ARTEM SHILOVETS - ТОЛПЫ КРИЧАТ
Toxi$ - HURTZ
Big Baby Tape, Aarne, Toxi$ - Ameli
HELLOVERCAVI, SODA LUV - СВАГА
kostromin - Моя голова винтом
Cheese People - Wake Up
Тима Белорусских - Мокрые кроссы
Тима Белорусских - Незабудка
ALMARY - До скорых встреч
КОСМОНАВТОВ НЕТ - МЯТОЙ
PIZZA - Улыбка
PIZZA - Оружие
Абрикоса - Влюбилась в друга
Miyagi & Эндшпиль - Summer time
Дора - Дорадура
Саша Айс, Софа Купер - Надо вот так
просто Лера - Хрущёвка
GAVRILINA - Жу Жу
Леонид Агутин - Остров
ALBLAK 52 - +7(952)812
Дора - Дора дура
Monelina - Девица
Макс Корж - Жить в кайф
SCIRENA - Конспект
Мэйби Бэйби - STAND UP
T-Fest, Скриптонит - Ламбада
N1NT3ND0 - Ламбада
Эндшпиль - 10
Бонд с Кнопкой - Кухни
T-Fest - Давай сконнектимся
КАЗАКИ ДЕЛАЮТ ХИТЫ - Мой ненаглядный
Татьяна Буланова - Мой ненаглядный
ICEGERGERT - Гектор
ICEGERGERT, SKY RAE - Наследство
Miyagi, HLOY - My Block
Мэйби Бэйби - Силиконовый Гном
Мэйби Бэйби - Неблагополучная Семья
IOWA, Ёлка - Яблоко
MilitaryHub - Легион
Kristina Si - Хочу
Григорий Стадник, Елена Стадник - Дружная семья - Дружная Россия
С-КОРПУС - Крещённые честью
I.L.A.Y., С.В.О.Й, Skyth27 - Курская битва 2.0
QKooK, Анастасия Гуня - Folk
Богдан Шувалов - Девушки России
ROMAN 7.62, Невский - Великая Держава
РОДНАЯ РЕЧЬ - Заря
KOVALEVA, Ратный - Русь
Айрен Коль - Из России с любовью
Future - Mask Off
Тайпан, LI ZA, Хорошуля - Не сломали
ПослеZавтра - пока Москва спала...
ТРАВМА - Закричу на весь мир
Акафист - Варяг
ARaveN, Аня Заболотникова, Юрий Голованов, ЯЖМИНА, LUBANЯ, Продюсерский центр Ленинградской области - Россия - это мы
АЗБУКА - РУССКИЕ ВПЕРЕД!
D. Stef, Chernysh, Nastya - Пятнашка
DDoZ - Шо С Лицом?
Сергей Хижняк - За Россию
NIGYL - BREAKTHROUGH
Gym Class Heroes, Adam Levine - Stereo Hearts (feat. Adam Levine)
Merk & Kremont, DNCE - Hands Up
Marwa Loud - Bad boy
Наша Победа, Оутен - А ДОМА ЛУЧШЕ
Aya Nakamura - Copines
ДАБРОВ, Max Tiaki - Идут музыканты
гречка - не моё
гречка - здесь были
Женя Трофимов - Самолеты
5УТРА - Давай сбежим (Искорки)
Дора - ЁК
Дора - Втюрилась
Ганвест - Кайфули
Полынь Folk, ГАЛЕЯ, КоленкорЪ, DAN3A, ПЕВЧАЯ, UNL1MET - Россия моя
Сын - БПЛА
ДАБРОВ - Поют
Big Baby Tape - Turbo (Majestic)
NLO - Танцы
maxxytren - ГИМН КАЧКОВ 2
Акафист - Русские вперёд
Винтаж, Bedanokov, Люай - Eva (Kavkaz remix)
Шкред, retroyse, chelsy smile, TEENWXVE, wxmac - Мало тебя
Lande, Matas - Россия
DDoZ - Трубы
Местный, Невский - From Russia
PXLXCH, prodby_teo - KATYUSHA ULTRA FUNK
Arath Rios, Y2K - LALALA
Filiz Kemal - Катюша
Каспийский Груз - Табор уходит в небо
HammAli & Navai - Птичка
Баста - На заре
Баста, Диана Арбенина, Александр Ф. Скляр, Сергей Бобунец, SunSay, Скриптонит - Сансара
Женя Трофимов, Комната культуры, Баста - Поезда
Стас Море - Обними меня, море
Олег Газманов - Бессмертный полк
Игорь Растеряев - Богатыри
MilitaryHub - До конца
madk1d - так по***
Макс Корж - Слово пацана
Макс Корж - Малый повзрослел
Макс Корж - 2 типа людей
Макс Корж - Горы по колено
ANNA ASTI - По барам
Зверобой - Волонтёрская
БЕРЕЗИНЫ - У моей России мамины глаза
Сюзанна Светличная - Ты живи моя страна
Елизавета Долженкова - Русская матрёшка
Олег Газманов - Ставрополье
Хор Турецкого - Русь моя
Маргарита Лисовина - Россия
Анастасия Макеева - Россия моя
Сергей Войтенко - Морошка
ЧАПАЕВ - Полюшка
Николай Емелин - Русь
MY-RO - Гармошечка
Кирилл Потылицын, Елена Морозова - Не будите русского медведя
Елизавета Долженкова - Белая лебёдушка
Алиса - Небо славян
Айрен Коль - Горы (Лезгинка)
Чибатуха - Московская кадриль
Виталий Синицын - Русский дух
Александр Деревянко, София Широковий - Гимн семье
Олег Газманов - Русский мир
Творческое объединение - Т - Гимн России #МыГордимсяТобой
Цветень - На речке
ЛАДКАНЯ - Порушка
СКАZKI - Калинка
Зверобой - Русская весна
Духовность - Ойся ты ойся
MASHA MAY - Волюшка
ABIEM Project - На горе-то калина
Ольга Бузова, Надежда Бабкина - Made in Russia
Galibri & Mavik - Ромашки
МК 5.45, Рома Жиган - Русские идут
MATRANG - Медуза
WANTARAM, I.L.A.Y., Ари100крат, Igor Tonika, NEPLOKH - БОЙСЯ
ГУДЗОН - Россия
АЗБУКА - ГРОМ КАСКАД
MIA BOYKA - Богатырская
SOLIDNAYA, SAKXRA - Пахнешь как
Black Eyed Peas - Rock That Body
Артур Пирожков - Само Собой
Willy William - Ego
Вектор А - Не вернусь
Konfuz, The Limba - Ты и Я
Xcho - Ты и Я
kobalt, Yeko - Boyna Galava
Sayfalse, Yb Wasg'ood, Ariis - Los Voltaje
Yb Wasg'ood, Ariis, MC PR - LUNA BALA
Teyno El Rey Del Marroneo - Shake It To The Max (Fly)
BEARWOLF, WXREAD - Гроза
Miyagi, KADI - Родная пой
Ратный - Не жалей
SKLЯR Алексей Скляренко - Санкции
MilitaryHub - Паутина на локте
Невский, I.L.A.Y., С.В.О.Й - Живыми или на щите
Градусы - Научиться бы не париться
Georgian Folk - Acharuli Gandagana
GIMS - NINAO
BEARWOLF - Один в поле воин
BEARWOLF - GODZILLA
SKLЯR Алексей Скляренко, Hanna11 - Экотуризм
SKLЯR Алексей Скляренко - Про праздники
SKLЯR Алексей Скляренко - День Победы
SKLЯR Алексей Скляренко - Русские изобретения
SKLЯR Алексей Скляренко - Про мультфильмы
SKLЯR Алексей Скляренко - Про китайские машины
SKLЯR Алексей Скляренко - Про блогеров
SKLЯR Алексей Скляренко - Про авто
SKLЯR Алексей Скляренко - Про ребёнка
Lumipa beats - Todo Es Relativo
SKLЯR Алексей Скляренко - Про новые профессии
Oliver Tree - Life Goes On
XXXTentacion - Jocelyn Flores
Tommy Cash - Espresso Macchiato
Sabi, Айгюн Кязымова - Я твой стресс (S.O.S. cover)
XXXTentacion - Look At Me!
XXXTentacion - SAD!
XXXTentacion - Hope
XXXTentacion - Moonlight
vxddka, Mari X - SI AI
Айни, Пабло, Mr Lambo - Май
Любэ - Комбат
Luis Fonsi, Daddy Yankee - Despacito
ATLXS, MEDUZA - PASSO BEM SOLTO
Шарлот - Мяу, мяу, мяу
I.L.A.Y. - Нижняя подсветка вкл
ГраУ - Оператор
DDoZ - Во славу России
Дайте танк (!) - Люди
AURORA - Cure For Me
AURORA - Runaway
Daddy Yankee, Snow - Con Calma
SHTIL - Лирика
SHTIL - Черный ворон
Scythermane, NXGHT!, Mc Fabinho da Osk - NUNCA MUDA?
paydak, Flu, lembsy - Suave
WOKAWÓNA - Он гениален
tet baby, 84 - Голая
Цветень - Где родился
Empire of Geese - Я гусь, мама-утка, смотри!
SHTIL - Оркестр Вагнер
DDoZ, SHLYAHOV - Слышишь?
Плётка - ЧВК Вагнер
АЗБУКА - PUTIN TEAM
Каспер - Туристы
SQWOZ BAB - TOKYO
MXZI - MONTAGEM TOMADA
Ирина Кайратовна - Чина
Любэ - За тебя, Родина-мать
HELVEGEN, РОДНАЯ РЕЧЬ - Родная земля
Ирина Кайратовна - Айдахар
Rasheeda - My Bubble Gum
The Hatters - Город поет (OST «Пророк. История Александра Пушкина»)
Charly Black - You're Perfect
Смешарики - Малиновая Лада
Смешарики - От винта!
DVRST, Игорь Скляр, Atomic Heart - Komarovo
DSPRITE - Погоди
10AGE - Нету интереса
VTORNIK - Money Rain
Nigahiga - Death Bed
Ted Fresco - Sunny Day
CKay, AX'EL, Dj Yo! - Love Nwantiti
KEAN DYSSO - Mask Off
Rude - Eternal Youth VIP
Afterclapp - Capitão de Areia
ptasinski, RJ Pasin - life force
Depressant, DEXTHBXY - Земля
Электрофорез, superkomfort - Фотограф
Adecvat_Production - За цвет голубых очей
NKOHA - White Night
WENARO, LXNER - Лёд
METAN - Перцовый баллон
MilitaryHub - КОТЁЛ
SHTIL - ESPAÑOLA
SHTIL - Русский солдат
SHTIL - Русский мир
shadowraze - astral step
My Moment Paradise - Chill Bill Lofi
Miyagi & Эндшпиль - Fire Man
DJ Snake, Selena Gomez, Ozuna, Cardi B - Taki Taki
Aaron Smith, Luvli, Krono - Dancin
Cheo Gallego - El Anciano y el Niño
Never Get Used To People - Life Letters
гречка - Люби меня люби
COMEDOZ, Павел Радонцев, Денис Гущин - Ямайка
RSAC, ELLA - NBA (Не мешай)
Madilyn Bailey - Señorita
Таня Терешина - Обломки чувств
PALC, CL1VA - Тараканы
Uma2rman - Папины дочки
Братья Грим - Кустурица
Казачки Кавказа - Русская рать
Slavik Pogosov - Монро
Jensen House - My Way
Natasha Morozova - Улетай На Крыльях Ветра
Стас Море - Движение Первых
Dynoro, Gigi D'Agostino - In My Mind
Klaas - Sweet Dreams
Timmy Trumpet, Savage - Freaks
Шарлот - Щека на щеку
Tesher - Jalebi Baby
CKay - love nwantiti (ah ah ah)
Эндшпиль - Малиновый рассвет
Bread Beatz - hey baby
stimulvibe - Жизнь общажная
Руки Вверх!, Лиза Роднянская - Песенка
R3HAB, A Touch Of Class - All Around The World (La La La)
MVTRIIIX, Kingpin Skinny Pimp - CALMNESS
Willy William - Voodoo Song
Aarne, BUSHIDO ZHO, Liza Evans - РЕВНУЮ
Clean Bandit, Sean Paul, Anne-Marie - Rockabye
Глад Валакас - Енотик-полоскун
Panjabi MC - Mundian to Bach Ke
Justin Leroy - STAY
Dj Mix Urbano - Levan Polkka
Lord Nekros - Bunny Girl Senpai
Marshmello, Anne-Marie - Friends
LISA - MONEY
Georgian Folk - Acharuli Gandagana
Sia, Sean Paul - Cheap Thrills
Jason Derulo - Take You Dancing
8D Tunes - Señorita (8D Audio)
Tiësto - Seavolution
Axeli - Software
twenty one pilots - Heathens
fenekot - Mockingbird
satirin - MATUSHKA ULTRAFUNK
Imagine Dragons, Lil Wayne - Believer
Dr. Dre, Snoop Dogg - The Next Episode
Ava Max - Kings & Queens
Смешарики - K.O.S.T.R.O.M.A. Phonk
asanrap, НОЛИК - чина нолик
Clean Bandit, Demi Lovato, Yxng Bane - Solo
Мурат Тхагалегов - Калым
Ёлка - Прованс
J Balvin, Willy William, Beyoncé - Mi Gente
Агас - Ромашка белая
MXZI - MONTAGEM TOMADA - Ultra Slowed
Aqua - Barbie Girl
Big Baby Tape - KARI
Natan, Тимати - Дерзкая
Kad1r - Balenciaga
IOWA - Улыбайся
Modern Group - Cheri cheri lady
Moamen Moaa - Makeba
Lil Jon & The East Side Boyz, Ying Yang Twins - Get Low
Аюб Вахарагов - Индийский чай
Phonk Killer, Kingpin Skinny Pimp - TRUNK
Bling Bling Bros - Yeah!
KRS-One - Sound Of Da Police
Masked Wolf - Astronaut In The Ocean
Smash Mouth - All Star
SAINt JHN - Roses
Afric Simone - Hafanana
Fazlija - Helikopter
will.i.am - I Like To Move It
DJ Remix Radio - Worth It
saigon nightmare - Davidich Smotra
OMFG - Hello
Stiven Starex - Открой глазки, открой глазаньки, вставай
Пика - Патимэйкер
Moreart, IHI - Я буду ебать
ГЛЕБАС, СУЕТА - ВАЦОК ПОЧУВСТВУЙ
DONI, Натали - Ты такой
Alex Ferrari - Bara Bara Bere Bere
Айдамир Мугу - Чёрные глаза
Султан-Ураган, Мурат Тхагалегов - На дискотеку!..
Алексей Воробьёв - Сумасшедшая
RaiM - Двигаться
Sylven - Бродяга
Олег Кензов - По кайфу
DJZRX - Not My Problem Funk (Slowed)
Элджей, FEDUK - Розовое вино
DJ CEREJASS, Sayfalse - BAD PARENTING FUNK
MC Xangai, DJ DAVY FELIPE, DJ TAK VADIÃO - Hoje em Dia é Difícil Encontrar
MC PL ALVES, MC Xangai, DJ Cleber, DJ LP Malvadão - Hoje em Dia É Difícil Encontrar
DJ BRYAN 7, DJIEGO, Maxximo Dj, MC GALAXIA, MC M4 - O Melhor no Que Faz 3.0
DJ BRYAN 7, DJIEGO, Maxximo Dj, MC GALAXIA, MC M4 - O Melhor no Que Faz 3.0
CYGO - Panda E
Launch13, MRR, Rodricci - EL ACABADO FUNK
Ariis - FUNK DO BOUNCE (Slowed)
Ariis - FUNK DO BOUNCE
Тимати, Рекорд Оркестр - Баклажан
Mr. President - Coco Jamboo
5sta Family - Зачем
DJ Snake - Taki Taki
PSY - Gangnam Style
Clean Bandit, Demi Lovato - Solo
Ёлка - На большом воздушном шаре
The Girly Team - Macarena
Блестящие - Восточные сказки
IOWA - Маршрутка
daryana - juice (original)
Стас Костюшкин - Женщина, я не танцую
Дора, Мэйби Бэйби - Барбисайз
Enina - кончил
SEREBRO - Между нами любовь
Magdy Haddad - Lets Boogyman
Generation 90er - Around the World
NCTS - NEXT!
Teriyaki Boyz - Tokyo Drift (Fast & Furious)
Nomi XD, VYRUS - BLAH!
J Balvin, Willy William - Mi Gente
KUSH LOVERS - 20К
ежанутый - Я ни человек
Aarne, BUSHIDO ZHO, ANIKV - Тесно
MAMA RUSSIA - Никола Тесла
Arlesy - KOMPA
speed up, Nightcore - i like the way you kiss me
Raf5q, Luke Willies - Kompa - Frozy
The Nightcore - Love Nwantiti (8D Slowed)
apillsinjuice - FREETATO
nyan.mp3 - И я такой пау пау пау
Сто-Личный Она-Нас, Betsy - Capybara
Fly Project - Toca Toca
DVRST - Close Eyes
Ed Sheeran - Shape of You
F4st - Carol of the Bells (Sped Up)
NBSPLV - The Lost Soul Down
Аким Апачев - Лето и арбалеты
listenreality - А эта песня про любовь
The Kiffness, Alugalug Cat 2.0 - Please Go Away
Ирина Дубцова - Люби меня долго
Geek Music - Gravity Falls Main Theme (From "Gravity Falls")
6YNTHMANE, 5sta Family, BAbyBoi - Zachem
Дайте танк (!) - Утро
Eternxlkz - SLAY!
BUSHIDO ZHO - далеко (большой Бушизм) [prod. by wex & heysubr]
INTERWORLD - METAMORPHOSIS
Dyan Dxddy - CUTE DEPRESSED
DVN - Можно я с тобой
Аня Клюква - Время молодых
Алиса Буслова - Двигаться вперёд
Стас Море - Будь первым!
Lida - Фото со звездой
Negro Can - Waka Waka (Esto Es África)
Morandi - Afrika
Inner Circle - Bad Boys (Theme from Cops)
METAN, Вектор А - Андеграунд
Lil Deal - Old Town Road
NLO - Звездолёт
Lemaier, Gulyashik, Qurorr - Мама удалила роблокс
NAVAI, MONA - Есенин
Каспер - Их там нет
SKWLKR - Лучшие в Аду
Big Baby Tape, Aarne - Supersonic
Niklas Dee, Junar, Menno - SugarCrash!
J Balvin, Skrillex - In Da Getto
The Rare Occasions - Notion
HELVEGEN - Слава роду
HELVEGEN - Ай да Россия
GONE.Fludd, IROH - Зашей
The Limba - Смузи
Олег Газманов, Хор центрального пограничного ансамбля ФСБ России - Вперёд Россия
FILV, Edmofo, Emma Peters, JVSTIN - Clandestina
TRITICUM - Petrunko 2.0
Indila - Ainsi bas la vida
БАНД'ЭРОС - Коламбия Пикчерз не представляет
Каста - Пупок внутри
SKLЯR Алексей Скляренко - Про итоги 2020 года
SKLЯR Алексей Скляренко - Про женщин в 30 лет
SKLЯR Алексей Скляренко - Про 30 лет
RADIO TAPOK - Гвардия Петра
RADIO TAPOK - Атака мертвецов
Кровосток - Цветы в вазе
SHTIL - WAGNER
Скриптонит, Райда - Baby mama
Badda Boo - Улетаю
Big Baby Tape - Trap Luv
V $ X V PRiNCE - Лирика
Скриптонит - Танцуй сама
алёна швец. - первое свидание
METAN - Паутина
АИГЕЛ - Татарин
PALC, BassnPanda - Тараканы
PALC - Совпадения
METAN - Шнурки
Fusion a.k.a EazyWin - Как казах
НАВЕРНОЕ ПОЭТ, ЯКОРЪ, EVEN CUTE - ЗАХОТЕЛ
НАВЕРНОЕ ПОЭТ, EVEN CUTE, ЯКОРЪ, derzko69 - РУССКАЯ ДУША
EVEN CUTE, НАВЕРНОЕ ПОЭТ, ЯКОРЪ - В РОССИИ ЖИТЬ ПИЗДАТО
Betsy, Мария Янковская - Sigma Boy
Скриптонит - не расслабляйся
SLAVA SKRIPKA - Бобр
Татьяна Куртукова - Ромашка-Василёк
Татьяна Куртукова - Одного
Татьяна Куртукова - Матушка
kizaru, ICEGERGERT - Fake ID
НАВЕРНОЕ ПОЭТ, ЯКОРЪ, EVEN CUTE, Ernest Merkel - ДА, Я РУССКИЙ
Кондрашов - Диктант
Каспийский Груз, Гио Пика - На белом
Miyagi & Andy Panda - Мало нам
Miyagi & Andy Panda - Utopia
Miyagi & Andy Panda - Kosandra
Miyagi & Andy Panda, Mav-d - Marmalade
Miyagi & Andy Panda - Патрон
Miyagi & Andy Panda - Там ревели горы
Miyagi & Andy Panda - Minor
Miyagi & Эндшпиль, NERAK - DLBM
Miyagi & Эндшпиль - Saloon
Miyagi & Эндшпиль - Санавабич
Miyagi & Эндшпиль - Половина моя
9 грамм, Miyagi & Эндшпиль - Рапапам
Miyagi & Эндшпиль, Рем Дигга - I Got Love
Miyagi - Sunshine
kavabanga Depo kolibri, Miyagi - Колибри
Miyagi, Andy Panda - Говори мне
Miyagi - Marlboro
Miyagi, HLOY, Даена - DAO
Miyagi - Captain
Melodic Music - My Medicine
Ilmari Hakkola - Bad Piggies Theme
ГЛАВНЫЙ РУС - РУСЫ ПРОТИВ ЯЩЕРОВ (СЛАВЯНСКИЙ ФОНК)
Trap Remix Guys - Giorno's Theme (From: JoJo's Bizarre Adventure: Golden Wind")
SKLЯR Алексей Скляренко - Про молодёжные слова
AY YOLA - Homay
Luka Jhonson - San Andreas
MDK - Press Start
joyful - chess
Фикс - Кожаные штаны
MORAXKILL, Astin Ray - VENCEDOR (SLOWED+REVERB)
Crazy Frog - Axel f"""

async def main():
    await init_db()
    
    tracks = parse_playlist(MY_PLAYLIST)
    print(f"🎵 Найдено треков: {len(tracks)}")
    
    added = 0
    for artist, title in tracks:
        genre, mood = auto_detect_genre(artist, title)
        await add_track(title=title, artist=artist, genre=genre, mood=mood)
        added += 1
        if added % 100 == 0:
            print(f"✅ Импортировано: {added}/{len(tracks)}")
    
    print(f"🎉 Готово! Импортировано {added} треков.")

if __name__ == '__main__':
    asyncio.run(main())