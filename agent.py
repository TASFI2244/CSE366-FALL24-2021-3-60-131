# agent.py
import pygame
import heapq

class Agent(pygame.sprite.Sprite):
    def __init__(self, environment, grid_size):
        super().__init__()
        self.image = pygame.Surface((grid_size, grid_size))
        self.image.fill((0, 0, 255))  # Agent color is blue
        self.rect = self.image.get_rect()
        self.grid_size = grid_size
        self.environment = environment
        self.position = [0, 0]  # Starting at the top-left corner of the grid
        self.rect.topleft = (0, 0)
        self.task_completed = 0
        self.completed_tasks = []
        self.path = []  # List of positions to follow
        self.moving = False  # Flag to indicate if the agent is moving
        self.total_path_cost = 0  # Track the total path cost

    def move(self):
        """Move the agent along the path."""
        if self.path:
            next_position = self.path.pop(0)
            self.position = list(next_position)
            self.rect.topleft = (self.position[0] * self.grid_size, self.position[1] * self.grid_size)
            self.total_path_cost += 1  # Increment total path cost with each move
            self.check_task_completion()
        else:
            self.moving = False  # Stop moving when path is exhausted

    def check_task_completion(self):
        """Check if the agent has reached a task location."""
        position_tuple = tuple(self.position)
        if position_tuple in self.environment.task_locations:
            task_number = self.environment.task_locations.pop(position_tuple)
            cost = self.total_path_cost
            self.task_completed += 1
            self.completed_tasks.append((task_number, cost))

    def find_nearest_task(self):
        """Find the nearest task using UCS."""
        nearest_task = None
        shortest_path = None
        for task_position in self.environment.task_locations.keys():
            path = self.ucs_find_path_to(task_position)
            if path:
                if not shortest_path or len(path) < len(shortest_path):
                    shortest_path = path
                    nearest_task = task_position
        if shortest_path:
            self.path = shortest_path[1:]  # Exclude the current position
            self.moving = True

    def ucs_find_path_to(self, target):
        """Find the shortest path to the target position using UCS."""
        start = tuple(self.position)
        goal = target
        queue = []
        heapq.heappush(queue, (0, [start]))  # (cost, path)
        visited = set()

        while queue:
            cost, path = heapq.heappop(queue)
            current = path[-1]
            if current == goal:
                return path
            if current in visited:
                continue
            visited.add(current)

            neighbors = self.get_neighbors(*current)
            for neighbor in neighbors:
                if neighbor not in visited:
                    new_path = list(path)
                    new_path.append(neighbor)
                    heapq.heappush(queue, (cost + 1, new_path))  # Uniform cost of 1
        return None  # No path found

    def get_neighbors(self, x, y):
        """Get walkable neighboring positions."""
        neighbors = []
        directions = [("up", (0, -1)), ("down", (0, 1)), ("left", (-1, 0)), ("right", (1, 0))]
        for _, (dx, dy) in directions:
            nx, ny = x + dx, y + dy
            if self.environment.is_within_bounds(nx, ny) and not self.environment.is_barrier(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
