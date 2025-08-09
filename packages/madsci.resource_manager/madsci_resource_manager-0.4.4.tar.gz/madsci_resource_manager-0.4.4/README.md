# MADSci Resource Manager

The MADSci Resource Manager provides tooling for tracking and managing the full lifecycle of all the resources (including assets, consumables, samples, containers, and any other physical object) used in an automated/autonomous laboratory.

## Notable Features

- Provides a robust Resource Type library and hierarchy for different "archetypes" of resource.
- Complete history for every tracked resource, and support for restoring deleted/removed resources
- Supports querying both active resources and history
- Provides a REST-based API compatible with the MADSci Resource Client (see [MADSci Clients](../madsci_client/README.md)).
- Enforces logical constraints on resources based on their properties, helping to catch errors like accidental virtual duplication of physical objects or nonsensical outcomes like negative quantities or overflows.

## Core Concepts

### Resource Types and the Type Hierarchy

MADSci Resource Manager supports various resource types, including:

- **Resource**: Base class for all resources.
- **Asset**: Tracked resources that aren't consumed (e.g., samples, labware).
- **Consumable**: Resources that are consumed (e.g., reagents, pipette tips).
- **Container**: Resources that can hold other resources (e.g., racks, plates).
- **Collection**: Containers that support random access.
- **Row**: Single-dimensional containers.
- **Grid**: Two-dimensional containers.
- **VoxelGrid**: Three-dimensional containers.
- **Slot**: A container that supports exactly zero or one child. Ideal for things like plate nests.
- **Stack**: Single-dimensional containers supporting LIFO access.
- **Queue**: Single-dimensional containers supporting FIFO access.
- **Pool**: Containers for holding consumables that are mixed or collocated.

You can define a resource using the ResourceDefinition types included in `madsci.common.types.resource_types.definitions`. These resource definitions can be used to query, create new, or attach to existing Resources.

## Usage

### Manager

To create and run a new MADSci Resource Manager, do the following in your MADSci lab directory:

- If you're not using docker compose, provision and configure an SQL database (we recommend and test against PostgreSQL, but other flavors may work).
- If you're using docker compose, create or add something like the following to your Lab's `compose.yaml`, defining your docker compose services for the ResourceManager and a PostgreSQL database to store your resources.

```yaml
name: madsci_example_lab
services:
  postgres:
    container_name: postgres
    image: postgres:17
    environment:
      - POSTGRES_USER=...
      - POSTGRES_PASSWORD=...
      - POSTGRES_DB=resources
    ports:
      - 5432:5432
  resource_manager:
    container_name: resource_manager
    image: ghcr.io/ad-sdl/madsci:latest
    build:
      context: ..
      dockerfile: Dockerfile
    environment:
      - USER_ID=1000
      - GROUP_ID=1000
    network_mode: host
    volumes:
      - /path/to/your/lab/directory:/home/madsci/lab/
      - .madsci:/home/madsci/.madsci/
    command: python -m madsci.resource_manager.resource_server
    depends_on:
      - postgres
```

```bash
# Create a new Resource Manager Definition
madsci manager add -t resource_manager
# Start the database and Resource Manager's REST Server
docker compose up
# OR
python -m madsci.resource_manager.resource_server
```

You should see a REST server started on the configured host and port. Navigate in your browser to the URL you configured (default: `http://localhost:8003/`) to see if it's working.

You can see up-to-date documentation on the endpoints provided by your resource manager, and try them out, via the swagger page served at `http://your-server-url-here/docs`.

### Client

Ensure you have access to the Resource Manager API and initialize the client:

```python
from madsci.client.resource_client import ResourceClient

url = "http://localhost:8003"
client = ResourceClient(url=url)
```

#### Adding a Resource

This saves a new resource to the resource database.

```python
from madsci.common.types.resource_types import Resource

resource = Resource(
    resource_name="Sample Resource",
    resource_class="sample",
)
added_resource = client.add_resource(resource)
print(added_resource)
```

#### Initializing a Resource

This saves a new resource to the resource database, if a matching resource doesn't exist already, or attaches to the existing resource if it does.

```python
from madsci.common.types.resource_types.definitions import ResourceDefinition

resource = ResourceDefinition(
  resource_name="Sample Resource",
  resource_class="sample",
)
initialized_resource = client.init_resource(resource)
print(intialized_resource)
```

#### Updating a Resource

Updates an existing resource.

```python
resource.resource_name = "Updated Sample Resource"
updated_resource = client.update_resource(resource)
print(updated_resource)
```

#### Getting a Resource

Get the current state of a given resource.

```python
fetched_resource = client.get_resource(resource_id=added_resource.resource_id)
print(fetched_resource)
```

#### Querying Resources

Query for a resource(s) that matches the provided parameters. Can specify whether to return multiple or require that there is a unique matching result.

```python
resources = client.query_resource(resource_class="sample", multiple=True)
for resource in resources:
    print(resource)
```

#### Removing a Resource

Delete a resource (the resource is preserved in the History table)

```python
removed_resource = client.remove_resource(resource_id=added_resource.resource_id)
print(removed_resource)
```

#### Querying Resource History

Get the entire history of a resource, from creation to deletion and every change in between.

```python
history = client.query_history(resource_id=added_resource.resource_id)
print(history)

import datetime

history = client.query_history(start_date=datetime.now(), change_type="Updated")
print(history)
```

#### Restoring a Deleted Resource

Restore the latest version of a deleted resource.

```python
restored_resource = client.restore_deleted_resource(resource_id=added_resource.resource_id)
print(restored_resource)
```

#### Pushing a Resource to a Stack, Queue, or Slot

Push a child resource onto a container, for containers that don't support random access.

```python
from madsci.common.types.resource_types import Stack

stack = Stack(resource_name="Sample Stack")
added_stack = client.add_resource(stack)
pushed_resource = client.push(resource=added_stack, child=added_resource)
print(pushed_resource)
```

#### Popping a Resource from a Stack, Queue, or Slot

Pop a child resource from a non-random access container.

```python
popped_resource, updated_stack = client.pop(resource=added_stack)
print(popped_resource, updated_stack)
```

#### Setting a Child Resource in a Container

Set a child at a specific key of a random access container.

```python
from madsci.common.types.resource_types import Grid

grid = Grid(resource_name="Sample Grid", columns=8, rows=12)
added_grid = client.add_resource(grid)
set_child_resource = client.set_child(resource=added_grid, key=(0, 0), child=added_resource)
print(set_child_resource)
```

#### Removing a Child Resource from a Container

Remove a child from a specific key of a random access container.

```python
removed_child_resource = client.remove_child(resource=added_grid, key=(0, 0))
print(removed_child_resource)
```

#### Setting the Quantity of a Consumable

Set the quantity of a consumable resource.

```python
from madsci.common.types.resource_types import Consumable

consumable = Consumable(resource_name="Sample Consumable", quantity=10)
added_consumable = client.add_resource(consumable)
updated_consumable = client.set_quantity(resource=added_consumable, quantity=20)
print(updated_consumable)
```

#### Changing the Quantity of a Consumable

Increase or decrease the quantity of a consumable by an amount.

```python
changed_consumable = client.change_quantity_by(resource=added_consumable, amount=5)
print(changed_consumable)
```

#### Increasing the Quantity of a Consumable

Strictly increase the quantity of a consumable by an amount.

```python
increased_consumable = client.increase_quantity(resource=added_consumable, amount=5)
print(increased_consumable)
```

#### Decreasing the Quantity of a Consumable

Strictly decrease the quantity of a consumable by an amount.

```python
decreased_consumable = client.decrease_quantity(resource=added_consumable, amount=5)
print(decreased_consumable)
```

#### Setting the Capacity of a Resource

Set the capacity (i.e., maximum quantity) of a resource.

```python
updated_capacity_resource = client.set_capacity(resource=added_consumable, capacity=50)
print(updated_capacity_resource)
```

#### Removing the Capacity Limit of a Resource

Remove the capacity (i.e., maximum quantity) of a resource.

```python
removed_capacity_resource = client.remove_capacity_limit(resource=added_consumable)
print(removed_capacity_resource)
```

#### Emptying a Resource

Empty a consumable or container resource.

```python
emptied_resource = client.empty(resource=added_consumable)
print(emptied_resource)
```

#### Filling a Resource

Fill a consumable resource.

```python
filled_resource = client.fill(resource=added_consumable)
print(filled_resource)
