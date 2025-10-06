import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import KanbanBoard from '../../../src/components/ui/KanbanBoard';

// Mock react-beautiful-dnd
jest.mock('react-beautiful-dnd', () => ({
  DragDropContext: ({ children }) => <div data-testid="drag-drop-context">{children}</div>,
  Droppable: ({ children, droppableId }) => 
    children({ 
      innerRef: jest.fn(), 
      droppableProps: { 'data-testid': `droppable-${droppableId}` },
      placeholder: <div data-testid="placeholder" />
    }, { isDraggingOver: false }),
  Draggable: ({ children, draggableId, index }) =>
    children({
      innerRef: jest.fn(),
      draggableProps: { 'data-testid': `draggable-${draggableId}` },
      dragHandleProps: {}
    }, { isDragging: false })
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>
  },
  AnimatePresence: ({ children }) => <div>{children}</div>
}));

describe('KanbanBoard Component', () => {
  const mockProps = {
    onTaskMove: jest.fn(),
    onTaskCreate: jest.fn(),
    onTaskUpdate: jest.fn(),
    onTaskDelete: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders default columns when no initial columns provided', () => {
    render(<KanbanBoard {...mockProps} />);
    
    expect(screen.getByText('To Do')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('Review')).toBeInTheDocument();
    expect(screen.getByText('Done')).toBeInTheDocument();
  });

  test('renders custom initial columns', () => {
    const customColumns = [
      { id: 'backlog', title: 'Backlog', color: 'from-gray-500 to-gray-600', tasks: [] },
      { id: 'active', title: 'Active', color: 'from-blue-500 to-blue-600', tasks: [] }
    ];

    render(<KanbanBoard {...mockProps} initialColumns={customColumns} />);
    
    expect(screen.getByText('Backlog')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.queryByText('To Do')).not.toBeInTheDocument();
  });

  test('displays task count for each column', () => {
    const columnsWithTasks = [
      {
        id: 'todo',
        title: 'To Do',
        color: 'from-blue-500 to-blue-600',
        tasks: [
          { id: 'task1', title: 'Task 1', description: 'Description 1' },
          { id: 'task2', title: 'Task 2', description: 'Description 2' }
        ]
      }
    ];

    render(<KanbanBoard {...mockProps} initialColumns={columnsWithTasks} />);
    
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  test('shows add task form when Add Task button is clicked', async () => {
    render(<KanbanBoard {...mockProps} />);
    
    const addTaskButton = screen.getAllByText('Add Task')[0];
    fireEvent.click(addTaskButton);
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Enter task title...')).toBeInTheDocument();
    });
  });

  test('creates new task when form is submitted', async () => {
    render(<KanbanBoard {...mockProps} />);
    
    const addTaskButton = screen.getAllByText('Add Task')[0];
    fireEvent.click(addTaskButton);
    
    const input = await screen.findByPlaceholderText('Enter task title...');
    fireEvent.change(input, { target: { value: 'New Task' } });
    
    const addButton = screen.getByText('Add');
    fireEvent.click(addButton);
    
    expect(mockProps.onTaskCreate).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'New Task'
      }),
      'todo'
    );
  });

  test('cancels task creation when Cancel button is clicked', async () => {
    render(<KanbanBoard {...mockProps} />);
    
    const addTaskButton = screen.getAllByText('Add Task')[0];
    fireEvent.click(addTaskButton);
    
    const cancelButton = await screen.findByText('Cancel');
    fireEvent.click(cancelButton);
    
    await waitFor(() => {
      expect(screen.queryByPlaceholderText('Enter task title...')).not.toBeInTheDocument();
    });
  });

  test('creates task when Enter key is pressed', async () => {
    render(<KanbanBoard {...mockProps} />);
    
    const addTaskButton = screen.getAllByText('Add Task')[0];
    fireEvent.click(addTaskButton);
    
    const input = await screen.findByPlaceholderText('Enter task title...');
    fireEvent.change(input, { target: { value: 'New Task' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
    
    expect(mockProps.onTaskCreate).toHaveBeenCalled();
  });

  test('renders tasks with correct information', () => {
    const columnsWithTasks = [
      {
        id: 'todo',
        title: 'To Do',
        color: 'from-blue-500 to-blue-600',
        tasks: [
          {
            id: 'task1',
            title: 'Task 1',
            description: 'Task description',
            priority: 'high',
            assignee: { name: 'John Doe' },
            dueDate: '2024-12-31'
          }
        ]
      }
    ];

    render(<KanbanBoard {...mockProps} initialColumns={columnsWithTasks} />);
    
    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task description')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  test('displays priority indicators correctly', () => {
    const columnsWithTasks = [
      {
        id: 'todo',
        title: 'To Do',
        color: 'from-blue-500 to-blue-600',
        tasks: [
          { id: 'task1', title: 'High Priority Task', priority: 'high' },
          { id: 'task2', title: 'Medium Priority Task', priority: 'medium' },
          { id: 'task3', title: 'Low Priority Task', priority: 'low' }
        ]
      }
    ];

    render(<KanbanBoard {...mockProps} initialColumns={columnsWithTasks} />);
    
    // Check that priority indicators are rendered (colored dots)
    const priorityDots = document.querySelectorAll('.bg-red-500, .bg-yellow-500, .bg-green-500');
    expect(priorityDots).toHaveLength(3);
  });

  test('shows empty state when column has no tasks', () => {
    render(<KanbanBoard {...mockProps} />);
    
    expect(screen.getAllByText('No tasks yet')).toHaveLength(4); // One for each default column
  });
});
