import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import Card from './Card';
import Button from './Button';

/**
 * Kanban Board Component - ReqDoc02 Phase 4
 * Features: Drag & drop, real-time updates, modern design
 */
const KanbanBoard = ({ 
  initialColumns = [], 
  onTaskMove, 
  onTaskCreate, 
  onTaskUpdate, 
  onTaskDelete 
}) => {
  const [columns, setColumns] = useState(initialColumns.length > 0 ? initialColumns : [
    {
      id: 'todo',
      title: 'To Do',
      color: 'from-blue-500 to-blue-600',
      tasks: []
    },
    {
      id: 'in-progress',
      title: 'In Progress',
      color: 'from-yellow-500 to-orange-500',
      tasks: []
    },
    {
      id: 'review',
      title: 'Review',
      color: 'from-purple-500 to-purple-600',
      tasks: []
    },
    {
      id: 'done',
      title: 'Done',
      color: 'from-green-500 to-green-600',
      tasks: []
    }
  ]);

  const [newTaskColumn, setNewTaskColumn] = useState(null);
  const [newTaskTitle, setNewTaskTitle] = useState('');

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const { source, destination } = result;
    
    if (source.droppableId === destination.droppableId && source.index === destination.index) {
      return;
    }

    const sourceColumn = columns.find(col => col.id === source.droppableId);
    const destColumn = columns.find(col => col.id === destination.droppableId);
    const task = sourceColumn.tasks[source.index];

    // Remove from source
    const newSourceTasks = [...sourceColumn.tasks];
    newSourceTasks.splice(source.index, 1);

    // Add to destination
    const newDestTasks = [...destColumn.tasks];
    newDestTasks.splice(destination.index, 0, task);

    // Update columns
    const newColumns = columns.map(col => {
      if (col.id === source.droppableId) {
        return { ...col, tasks: newSourceTasks };
      }
      if (col.id === destination.droppableId) {
        return { ...col, tasks: newDestTasks };
      }
      return col;
    });

    setColumns(newColumns);
    onTaskMove?.(task.id, source.droppableId, destination.droppableId, destination.index);
  };

  const handleCreateTask = (columnId) => {
    if (!newTaskTitle.trim()) return;

    const newTask = {
      id: `task-${Date.now()}`,
      title: newTaskTitle,
      description: '',
      assignee: null,
      priority: 'medium',
      dueDate: null,
      createdAt: new Date().toISOString()
    };

    const newColumns = columns.map(col => {
      if (col.id === columnId) {
        return { ...col, tasks: [...col.tasks, newTask] };
      }
      return col;
    });

    setColumns(newColumns);
    setNewTaskTitle('');
    setNewTaskColumn(null);
    onTaskCreate?.(newTask, columnId);
  };

  const TaskCard = ({ task, index }) => (
    <Draggable draggableId={task.id} index={index}>
      {(provided, snapshot) => (
        <motion.div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={`mb-3 ${snapshot.isDragging ? 'rotate-3 scale-105' : ''}`}
          whileHover={{ scale: 1.02 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <Card 
            variant="default" 
            className={`p-4 cursor-grab active:cursor-grabbing ${
              snapshot.isDragging ? 'shadow-2xl ring-2 ring-blue-500/50' : ''
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="font-semibold text-gray-900 text-sm">{task.title}</h4>
              <div className="flex items-center space-x-1">
                {task.priority === 'high' && (
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                )}
                {task.priority === 'medium' && (
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                )}
                {task.priority === 'low' && (
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                )}
              </div>
            </div>
            
            {task.description && (
              <p className="text-gray-600 text-xs mb-3 line-clamp-2">{task.description}</p>
            )}
            
            <div className="flex items-center justify-between">
              {task.assignee && (
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs font-bold">
                      {task.assignee.name.charAt(0)}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">{task.assignee.name}</span>
                </div>
              )}
              
              {task.dueDate && (
                <span className="text-xs text-gray-500">
                  {new Date(task.dueDate).toLocaleDateString()}
                </span>
              )}
            </div>
          </Card>
        </motion.div>
      )}
    </Draggable>
  );

  return (
    <div className="w-full h-full p-6">
      <motion.div 
        className="mb-6"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
          Project Board
        </h2>
        <p className="text-gray-600">Drag and drop tasks to update their status</p>
      </motion.div>

      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 h-full">
          {columns.map((column, columnIndex) => (
            <motion.div
              key={column.id}
              className="flex flex-col h-full"
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: columnIndex * 0.1 }}
            >
              <Card variant="glass" className="flex flex-col h-full">
                {/* Column Header */}
                <div className="p-4 border-b border-white/20">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 bg-gradient-to-r ${column.color} rounded-full`}></div>
                      <h3 className="font-semibold text-gray-900">{column.title}</h3>
                    </div>
                    <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                      {column.tasks.length}
                    </span>
                  </div>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setNewTaskColumn(column.id)}
                    className="w-full justify-center"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Add Task
                  </Button>
                </div>

                {/* New Task Form */}
                <AnimatePresence>
                  {newTaskColumn === column.id && (
                    <motion.div
                      className="p-4 border-b border-white/20"
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <input
                        type="text"
                        placeholder="Enter task title..."
                        value={newTaskTitle}
                        onChange={(e) => setNewTaskTitle(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm mb-3"
                        autoFocus
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            handleCreateTask(column.id);
                          }
                        }}
                      />
                      <div className="flex space-x-2">
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => handleCreateTask(column.id)}
                        >
                          Add
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setNewTaskColumn(null);
                            setNewTaskTitle('');
                          }}
                        >
                          Cancel
                        </Button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Tasks */}
                <Droppable droppableId={column.id}>
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className={`flex-1 p-4 transition-colors duration-200 ${
                        snapshot.isDraggingOver ? 'bg-blue-50/50' : ''
                      }`}
                    >
                      <AnimatePresence>
                        {column.tasks.map((task, index) => (
                          <TaskCard key={task.id} task={task} index={index} />
                        ))}
                      </AnimatePresence>
                      {provided.placeholder}
                      
                      {column.tasks.length === 0 && (
                        <motion.div
                          className="text-center py-8 text-gray-400"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.5 }}
                        >
                          <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                          </svg>
                          <p className="text-sm">No tasks yet</p>
                        </motion.div>
                      )}
                    </div>
                  )}
                </Droppable>
              </Card>
            </motion.div>
          ))}
        </div>
      </DragDropContext>
    </div>
  );
};

export default KanbanBoard;
