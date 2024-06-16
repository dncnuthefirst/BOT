import discord
from discord.ext import commands
import random
# Initialize Discord client
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables for the game
games = {}
number_emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
mine_emoji = "🧨"
uncovered_emoji = "❔"  # Using a white question mark because why not

class MinesweeperGame:
    def __init__(self, rows, cols, num_mines):
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        self.grid = self.initialize_grid(rows, cols, num_mines)
        self.visible_grid = [[uncovered_emoji for _ in range(cols)] for _ in range(rows)]
        self.game_over = False
        self.message = None  # To store the message displaying the grid

    def initialize_grid(self, rows, cols, num_mines):
        grid = [['0' for _ in range(cols)] for _ in range(rows)]
        placed_mines = 0

        while placed_mines < num_mines:
            row = random.randint(0, rows - 1)
            col = random.randint(0, cols - 1)

            if grid[row][col] != '*':
                grid[row][col] = '*'
                placed_mines += 1

                # Update adjacent cells
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if 0 <= row + dr < rows and 0 <= col + dc < cols and grid[row + dr][col + dc] != '*':
                            grid[row + dr][col + dc] = str(int(grid[row + dr][col + dc]) + 1)

        return grid

    def uncover_cells(self, row, col):
        if self.visible_grid[row][col] == uncovered_emoji:
            self.visible_grid[row][col] = self.grid[row][col]
            if self.grid[row][col] == '0':
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if 0 <= row + dr < self.rows and 0 <= col + dc < self.cols:
                            self.uncover_cells(row + dr, col + dc)

    def check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.visible_grid[r][c] == uncovered_emoji and self.grid[r][c] != '*':
                    return False
        return True

# Command to start a new Minesweeper game
@bot.command(name='minesweeper')
async def start_minesweeper(ctx, rows: int, cols: int, num_mines: int):

    if (rows < 1 or cols < 1 or num_mines < 1 or num_mines >= rows * cols):
        await ctx.send("Invalid input! Please ensure rows, columns, and number of mines are positive and valid.")
        return

    # Create a new Minesweeper game instance
    game = MinesweeperGame(rows, cols, num_mines)
    games[ctx.channel.id] = game

    # Print the initial grid to the channel
    if (rows * cols) > 4000:
        await ctx.send("The grid is too large to display not because I don't have nitro because discord can't give me more than 4000 characters ;(")
        return
    await ctx.send("minesweeper time. \nUse `!uncover row col` to uncover a cell from left-right and up-down.\nUse `!end` to end the game if you are lazy.\n")
    game.message = await print_grid(ctx, game.visible_grid)

# Command to uncover a cell in Minesweeper
@bot.command(name='uncover')
async def uncover_cell(ctx, row: int, col: int):
    if ctx.channel.id not in games:
        await ctx.send("Shocking, I know. But you cant uncover a cell in a game that doesnt exist. \nUse `!minesweeper 5 5 3 \n")
        return

    game = games[ctx.channel.id]

    if game.game_over:
        await ctx.send("mmm game over already, use \n !minesweeper 5 5 3 \n for example to start a new game.")
        return

    if row < 0 or row - 1 >= game.rows or col < 0 or col - 1 >= game.cols:
        await ctx.send("This is 2D not 4D how are u getting these numbers?")
        return

    if game.grid[row - 1][col - 1] == '*':
        game.game_over = True
        await ctx.send("Game over mine hit u.")
        await print_grid(ctx, game.grid, game_over=True)
    else:
        game.uncover_cells(row - 1, col - 1)
        if game.check_win():
            game.game_over = True
            await ctx.send("Wow you the bomb expert")
            await print_grid(ctx, game.grid)
        else:
            await print_grid(ctx, game.visible_grid)

# Command to end the Minesweeper game
@bot.command(name='end')
async def end_minesweeper(ctx):
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        await ctx.send("end game finish yay.")
    else:
        await ctx.send("ending something that doesnt exist? nuh uh")

# Function to print the Minesweeper grid in Discord
async def print_grid(ctx, grid, game_over=False):
    output = ''
    for row in grid:
        output += ''.join([
            mine_emoji if cell == '*' and game_over else
            uncovered_emoji if cell == uncovered_emoji else
            number_emojis[int(cell)] if cell.isdigit() else cell 
            for cell in row
        ]) + '\n'
    game = games[ctx.channel.id]
    if game.message:
        await game.message.edit(content=output)
    else:
        game.message = await ctx.send(output)

# Event handler for bot ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# Wait did u see this token uhh please have mercy on me
TOKEN = "MTIyNzU0NjYyMjQ1Njc1ODI5Mg.G1HAuA.HDFIv1vrDOfuzla5yRaDToWKTi161ipIPh1w44"
bot.run(TOKEN)
