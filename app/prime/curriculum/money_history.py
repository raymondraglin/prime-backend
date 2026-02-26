from app.prime.curriculum.models import SubjectId, HistoryEvent


def get_history_of_money() -> list[HistoryEvent]:
    """
    History of money from early exchange and barter to modern digital forms.
    """
    events: list[HistoryEvent] = []

    # 1) Early exchange and barter
    events.append(
        HistoryEvent(
            id="money_hist_barter",
            title="Early Exchange and Barter",
            era="Prehistoric / Ancient",
            approx_date="Before formal money, in early human societies",
            location="Various regions",
            description=(
                "Before formal money, people exchanged goods and services directly. "
                "This is called barter: trading one thing for another, such as grain for tools "
                "or animals for clothing."
            ),
            significance=(
                "Barter works for simple trades but makes it hard to compare values, store value "
                "over time, or make change. These problems pushed societies toward creating money."
            ),
            related_subjects=[SubjectId.MONEY_FOUNDATIONS_HISTORY],
            related_lessons=[],
        )
    )

    # 2) Commodity money
    events.append(
        HistoryEvent(
            id="money_hist_commodity",
            title="Commodity Money",
            era="Ancient",
            approx_date="As early civilizations grew",
            location="Various regions",
            description=(
                "Many early societies began using valuable commodities as money, such as cattle, "
                "grain, shells, or pieces of metal. These items were widely accepted and could be "
                "used to settle debts or pay for goods."
            ),
            significance=(
                "Commodity money was a first step toward commonly accepted things that represent value. "
                "However, these items could be bulky, hard to divide evenly, or vary in quality."
            ),
            related_subjects=[SubjectId.MONEY_FOUNDATIONS_HISTORY],
            related_lessons=[],
        )
    )

    # 3) Early metal money and coins
    events.append(
        HistoryEvent(
            id="money_hist_early_coins",
            title="Early Metal Money and Coins",
            era="Ancient",
            approx_date="c. 600–300 BCE",
            location="Lydia, China, and other regions",
            description=(
                "Some of the earliest coins were issued in Lydia (in what is now Turkey) and in ancient "
                "China. These coins were made of metal and stamped with symbols to show their value and "
                "authority."
            ),
            significance=(
                "Coins made it easier to carry, count, and compare value. Standardized metal pieces "
                "allowed people to make change and price goods more precisely, much like using discrete "
                "dollar and cent amounts today."
            ),
            related_subjects=[SubjectId.MONEY_FOUNDATIONS_HISTORY],
            related_lessons=[
                "math_fnd_money_fractions",
                "math_fnd_decimals_basic",
                "math_fnd_word_problems_money_basic",
            ],
        )
    )

    # 4) Classical and medieval coin economies
    events.append(
        HistoryEvent(
            id="money_hist_classical_coins",
            title="Classical and Medieval Coin Economies",
            era="Classical to Medieval",
            approx_date="c. 500 BCE–1500 CE",
            location="Mediterranean, Europe, and beyond",
            description=(
                "Greek, Roman, and later European societies built long-lasting coin-based economies. "
                "Governments issued coins of different denominations, often in gold, silver, or copper."
            ),
            significance=(
                "Coins became a normal part of daily life for paying wages, buying goods, and collecting "
                "taxes. Issues like coin debasement (reducing the precious metal content) showed how "
                "political choices could affect the value of money."
            ),
            related_subjects=[SubjectId.MONEY_FOUNDATIONS_HISTORY],
            related_lessons=[
                "math_fnd_money_fractions",
                "math_fnd_word_problems_money_basic",
            ],
        )
    )

    # 5) Early paper money
    events.append(
        HistoryEvent(
            id="money_hist_paper_early",
            title="Early Paper Money",
            era="Medieval to Early Modern",
            approx_date="c. 900–1700 CE",
            location="China, then Europe and the Americas",
            description=(
                "In China, especially during the Song dynasty, governments and merchants began using paper "
                "money as receipts or promises for metal coins or goods stored elsewhere. Later, European "
                "states and colonies also issued paper notes."
            ),
            significance=(
                "Paper money represented claims on value instead of value in the paper itself. Different "
                "note denominations made it natural to think in units like 1, 5, 10, or 100, much like "
                "today's dollar bills and decimal amounts."
            ),
            related_subjects=[SubjectId.MONEY_FOUNDATIONS_HISTORY],
            related_lessons=[
                "math_fnd_money_fractions",
                "math_fnd_decimals_basic",
                "math_fnd_word_problems_money_basic",
            ],
        )
    )

    # 6) Banks and banknotes
    events.append(
        HistoryEvent(
            id="money_hist_banks_banknotes",
            title="Banks and Banknotes",
            era="Early Modern",
            approx_date="c. 1600–1900 CE",
            location="Europe and the Americas",
            description=(
                "Goldsmiths and early bankers accepted deposits of coins and issued written receipts. "
                "Over time, these receipts evolved into banknotes issued by banks and later by central "
                "banks on behalf of governments."
            ),
            significance=(
                "Banks became institutions that held money, created credit, and helped move value across "
                "distance. Banknotes were easier to move than large amounts of coins and became a central "
                "part of national money systems."
            ),
            related_subjects=[SubjectId.MONEY_FOUNDATIONS_HISTORY],
            related_lessons=[
                "math_fnd_decimals_basic",
                "math_fnd_word_problems_money_basic",
            ],
        )
    )

    # 7) Gold and silver standards and their decline
    events.append(
        HistoryEvent(
            id="money_hist_gold_silver_standards",
            title="Gold and Silver Standards and Their Decline",
            era="Modern",
            approx_date="c. 1800–1900s CE",
            location="Many industrializing countries",
            description=(
                "Many countries tied their currencies to fixed amounts of gold or silver, promising "
                "that paper money could be exchanged for precious metal. Over the twentieth century, "
                "most nations moved away from strict gold or silver backing."
            ),
            significance=(
                "Moving from metal-backed money to fiat money meant that the value of money depended more "
                "on trust in governments and central banks than on holding gold or silver reserves."
            ),
            related_subjects=[SubjectId.MONEY_FOUNDATIONS_HISTORY],
            related_lessons=[
                "math_fnd_decimals_basic",
            ],
        )
    )

    # 8) Electronic and digital money
    events.append(
        HistoryEvent(
            id="money_hist_electronic",
            title="Electronic and Digital Money",
            era="Late Modern",
            approx_date="1900s–early 2000s CE",
            location="Global",
            description=(
                "With electronic banking, payment cards, and online transfers, much money began to move "
                "as entries in computer systems instead of as coins or paper. Salaries, bills, and everyday "
                "purchases increasingly flowed through electronic networks."
            ),
            significance=(
                "Money became more abstract and less tied to physical objects. Balances, transfers, and "
                "prices still rely on decimals and fractions, but the 'tokens' are now digital records."
            ),
            related_subjects=[SubjectId.MONEY_FOUNDATIONS_HISTORY],
            related_lessons=[
                "math_fnd_decimals_basic",
                "math_fnd_word_problems_money_basic",
            ],
        )
    )

    # 9) Modern digital payments and beyond
    events.append(
        HistoryEvent(
            id="money_hist_modern_digital",
            title="Modern Digital Payments and Beyond",
            era="Contemporary",
            approx_date="2000s–present",
            location="Global",
            description=(
                "Today, people use mobile payments, online platforms, and other digital systems to send "
                "money instantly across the world. New forms of digital assets and programmable money have "
                "also emerged."
            ),
            significance=(
                "These systems build directly on decimal-based money and electronic records, and they set "
                "the stage for future lessons about economics, investing, and how financial systems work."
            ),
            related_subjects=[SubjectId.MONEY_FOUNDATIONS_HISTORY],
            related_lessons=[
                "math_fnd_decimals_basic",
                "math_fnd_word_problems_money_basic",
            ],
        )
    )

    return events
