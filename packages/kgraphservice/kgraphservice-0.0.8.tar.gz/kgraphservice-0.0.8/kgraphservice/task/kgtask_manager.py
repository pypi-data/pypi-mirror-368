

# manager for KGTask objects
# queries to get details of the kgtasks

# changes to the tasks would go through an execution engine

# crud operations on kgtasks outside of the execution engine should be disallowed
# to be enforced by the kgservice impl, such as within vital-agent-rest/vital-agent-resource-rest
# execution engine can pass JWT to kgservice impl with claims/rights to update tasks to enable modifications
# claims to include the execution service engine id, which would match
# the assigned task execution engine id, such that that engine owns the task and is allowed to change it
# this id to be assigned when task is created or is empty until manager assigns an engine to it
# this id is for the type of engine, not the instance of an engine
# which means an engine would need to coordinate among the instances such
# that the instances wouldnt conflict when modifying a task
# there can be an additional assignment of an engine to an instance for the one that
# is executing the task to de-conflict it
# kgservice would need to enable transactional changes to objects like this assignment

# perhaps use separate lock table similar to account lock table for enforcing atomic task modification
# i.e. get lock (via table) or fail, make change, release lock
# this would be in vital-agent-rest as all kgraph changes are routed here

# potentially have separate task assignment object with kgtask having UIR property pointing to the current
# instance of this, so transaction would be limited to modifying kgtask object (and or these two objects)

# extraction service being one such execution engine

# modifications to tasks can trigger notifications to subscribers of changes
# which are delivered by paths such as bridged messages
# currently bridged messages target a user session whereas a recurring background
# task is not tied to an active user session, so this may need to
# target a haley session and channel such as #task/#kgtask which could send the notification
# to an agent to react to it
# minor update to haley saas server may be necessary for bridge messages with haley session



