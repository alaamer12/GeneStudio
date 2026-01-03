# PyPika Usage Guide for GeneStudio

PyPika is a Python SQL query builder that provides a clean, programmatic way to construct SQL queries. It helps avoid SQL injection vulnerabilities and makes queries more maintainable.

## Installation

PyPika is included in our requirements.txt:
```
pypika>=0.48.9
```

## Basic Usage

### Import
```python
from pypika import Query, Table, Field, functions as fn
```

### Define Tables
```python
# Define table references
projects = Table('projects')
sequences = Table('sequences')
analyses = Table('analyses')
settings = Table('settings')
activity_log = Table('activity_log')
```

## Query Examples

### SELECT Queries

#### Simple Select
```python
# Instead of: "SELECT * FROM projects WHERE status = 'active'"
query = Query.from_(projects).select('*').where(projects.status == 'active')
sql, params = query.get_sql(quote_char=None, paramstyle='qmark')
```

#### Select with Joins
```python
# Get sequences with project information
query = (Query
    .from_(sequences)
    .join(projects).on(sequences.project_id == projects.id)
    .select(sequences.header, sequences.length, projects.name.as_('project_name'))
    .where(projects.status == 'active')
)
```

#### Aggregations
```python
# Project statistics
query = (Query
    .from_(projects)
    .select(
        fn.Count('*').as_('total_projects'),
        fn.Count(Case().when(projects.status == 'active', 1)).as_('active_projects'),
        fn.Sum(projects.sequence_count).as_('total_sequences')
    )
)
```

### INSERT Queries

#### Simple Insert
```python
# Instead of manual parameter counting
query = (Query
    .into(projects)
    .columns('id', 'name', 'type', 'description', 'created_date', 'status')
    .insert(next_id, name, project_type, description, created_date, status)
)
```

#### Insert with Multiple Values
```python
query = (Query
    .into(sequences)
    .columns('id', 'project_id', 'header', 'sequence', 'sequence_type')
    .insert(1, 1, 'Seq1', 'ATCG', 'dna')
    .insert(2, 1, 'Seq2', 'GCTA', 'dna')
)
```

### UPDATE Queries

#### Simple Update
```python
query = (Query
    .update(projects)
    .set('modified_date', datetime.now())
    .set('status', 'completed')
    .where(projects.id == project_id)
)
```

#### Conditional Updates
```python
query = (Query
    .update(projects)
    .set('sequence_count', projects.sequence_count + 1)
    .where(projects.id == project_id)
)
```

### DELETE Queries

#### Simple Delete
```python
query = Query.from_(projects).delete().where(projects.id == project_id)
```

#### Cascading Delete
```python
# Delete analyses first, then sequences, then project
analyses_query = Query.from_(analyses).delete().where(analyses.project_id == project_id)
sequences_query = Query.from_(sequences).delete().where(sequences.project_id == project_id)
projects_query = Query.from_(projects).delete().where(projects.id == project_id)
```

## Advanced Features

### Subqueries
```python
# Find projects with more than 10 sequences
subquery = (Query
    .from_(sequences)
    .select(sequences.project_id)
    .groupby(sequences.project_id)
    .having(fn.Count('*') > 10)
)

main_query = (Query
    .from_(projects)
    .select('*')
    .where(projects.id.isin(subquery))
)
```

### Case Statements
```python
from pypika import Case

query = (Query
    .from_(analyses)
    .select(
        analyses.id,
        Case()
        .when(analyses.status == 'completed', 'Success')
        .when(analyses.status == 'failed', 'Error')
        .else_('In Progress')
        .as_('status_display')
    )
)
```

### Date Functions
```python
# Recent projects (last 7 days)
query = (Query
    .from_(projects)
    .select('*')
    .where(projects.created_date >= fn.Now() - fn.Interval(days=7))
)
```

## Integration with Repository Pattern

### Example Repository Method with PyPika
```python
def get_active_projects_with_stats(self) -> List[Project]:
    """Get active projects with sequence/analysis counts using PyPika."""
    projects = Table('projects')
    sequences = Table('sequences')
    analyses = Table('analyses')
    
    query = (Query
        .from_(projects)
        .left_join(sequences).on(sequences.project_id == projects.id)
        .left_join(analyses).on(analyses.project_id == projects.id)
        .select(
            projects.star,
            fn.Count(sequences.id.distinct()).as_('actual_sequence_count'),
            fn.Count(analyses.id.distinct()).as_('actual_analysis_count')
        )
        .where(projects.status == 'active')
        .groupby(projects.id)
        .orderby(projects.modified_date, order=Order.desc)
    )
    
    sql, params = query.get_sql(quote_char=None, paramstyle='qmark')
    result = self._execute_query(sql, params)
    
    return [Project.from_dict(row) for row in result]
```

## Benefits of Using PyPika

1. **Type Safety**: Catch errors at development time
2. **SQL Injection Prevention**: Automatic parameter binding
3. **Readability**: More readable than string concatenation
4. **Maintainability**: Easy to modify complex queries
5. **Database Agnostic**: Works with multiple database engines
6. **IDE Support**: Better autocomplete and refactoring

## Migration Strategy

When updating existing repositories:

1. **Gradual Migration**: Update methods one at a time
2. **Keep Tests**: Ensure existing tests still pass
3. **Complex Queries First**: Start with the most complex queries that benefit most
4. **Simple Queries Last**: Basic CRUD operations can be migrated last

## Best Practices

1. **Define Tables Once**: Create table objects at module level
2. **Use Meaningful Aliases**: Make query results clear
3. **Parameterize Values**: Always use parameters, never string interpolation
4. **Test Queries**: Verify generated SQL matches expectations
5. **Document Complex Queries**: Add comments for business logic

## Example: Complete Repository Method

```python
from pypika import Query, Table, functions as fn, Order

class ProjectRepository(BaseRepository[Project]):
    def __init__(self):
        super().__init__()
        self.projects = Table('projects')
        self.sequences = Table('sequences')
        self.analyses = Table('analyses')
    
    def search_projects_with_stats(self, search_term: str, 
                                  status_filter: Optional[str] = None) -> List[Project]:
        """Search projects with statistics using PyPika."""
        
        # Build base query
        query = (Query
            .from_(self.projects)
            .left_join(self.sequences).on(self.sequences.project_id == self.projects.id)
            .left_join(self.analyses).on(self.analyses.project_id == self.projects.id)
            .select(
                self.projects.star,
                fn.Count(self.sequences.id.distinct()).as_('sequence_count'),
                fn.Count(self.analyses.id.distinct()).as_('analysis_count')
            )
            .where(
                (self.projects.name.like(f'%{search_term}%')) |
                (self.projects.description.like(f'%{search_term}%'))
            )
            .groupby(self.projects.id)
            .orderby(self.projects.modified_date, order=Order.desc)
        )
        
        # Add status filter if provided
        if status_filter:
            query = query.where(self.projects.status == status_filter)
        
        # Execute query
        sql, params = query.get_sql(quote_char=None, paramstyle='qmark')
        result = self._execute_query(sql, params)
        
        return [Project.from_dict(row) for row in result]
```

This approach makes queries more maintainable and reduces the likelihood of SQL-related bugs.