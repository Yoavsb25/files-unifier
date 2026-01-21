# PDF Merger - Architecture Diagram

This document contains Mermaid diagrams showing the architecture and workflow of the PDF Merger project.

## System Architecture & Data Flow

```mermaid
flowchart TB
    Start([User Starts Application]) --> CheckArgs{Command Line<br/>Arguments?}
    
    CheckArgs -->|Yes| CLI[CLI Mode<br/>command_line.py]
    CheckArgs -->|No| Interactive[Interactive Mode<br/>interactive.py]
    
    CLI --> ParseArgs[Parse Arguments<br/>argparse]
    Interactive --> GetInput[Get User Input<br/>Prompts for paths]
    
    ParseArgs --> ValidateCLI[validate_paths]
    GetInput --> ValidateInteractive[validate_file<br/>validate_folder]
    
    ValidateCLI -->|Invalid| Exit1[Exit with Error]
    ValidateInteractive -->|Invalid| Retry[Prompt Again]
    Retry --> GetInput
    
    ValidateCLI -->|Valid| Process[process_file]
    ValidateInteractive -->|Valid| Process
    
    Process --> CreateOutput[Create Output Folder]
    CreateOutput --> ReadFile[read_data_file]
    
    ReadFile --> DetectType{File Type?}
    DetectType -->|CSV| ReadCSV[read_csv<br/>Detect Delimiter]
    DetectType -->|Excel| ReadExcel[read_excel<br/>pandas]
    
    ReadCSV --> IterateRows[Iterate Rows]
    ReadExcel --> IterateRows
    
    IterateRows --> ProcessRow[process_row]
    
    ProcessRow --> ParseData[parse_serial_numbers<br/>Split comma-separated]
    ParseData --> FindPDFs[For each filename:<br/>find_pdf_file]
    
    FindPDFs --> SearchPDF[Search Source Folder<br/>Case-insensitive match]
    SearchPDF -->|Found| AddToList[Add to PDF List]
    SearchPDF -->|Not Found| LogWarning[Log Warning]
    
    AddToList --> CheckMore{More<br/>Filenames?}
    LogWarning --> CheckMore
    CheckMore -->|Yes| FindPDFs
    CheckMore -->|No| CheckPDFs{Any PDFs<br/>Found?}
    
    CheckPDFs -->|No| SkipRow[Skip Row<br/>Return False]
    CheckPDFs -->|Yes| MergePDFs[merge_pdfs]
    
    MergePDFs --> CreateWriter[Create PdfWriter]
    CreateWriter --> ReadEachPDF[For each PDF:<br/>PdfReader + Add Pages]
    ReadEachPDF --> WriteOutput[Write Merged PDF<br/>merged_row_N.pdf]
    
    WriteOutput --> Success{Success?}
    Success -->|Yes| IncrementSuccess[Increment Success Count]
    Success -->|No| AddFailed[Add to Failed Rows]
    
    IncrementSuccess --> NextRow{More<br/>Rows?}
    AddFailed --> NextRow
    SkipRow --> NextRow
    
    NextRow -->|Yes| IterateRows
    NextRow -->|No| ReturnResult[Return ProcessingResult]
    
    ReturnResult --> DisplaySummary[Display Summary<br/>Total/Success/Failed]
    DisplaySummary --> End([End])
    
    Exit1 --> End
    
    style Start fill:#e1f5ff
    style End fill:#e1f5ff
    style Process fill:#fff4e1
    style MergePDFs fill:#ffe1f5
    style ValidateCLI fill:#e1ffe1
    style ValidateInteractive fill:#e1ffe1
    style ReadFile fill:#f0e1ff
    style FindPDFs fill:#ffe1f0
```

## Component Architecture

```mermaid
graph TB
    subgraph "Entry Points"
        Main[main.py<br/>Entry Point]
        CLI[cli/command_line.py<br/>CLI Interface]
        Interactive[cli/interactive.py<br/>Interactive Interface]
    end
    
    subgraph "Core Processing"
        Processor[processor.py<br/>process_file<br/>process_row<br/>ProcessingResult]
    end
    
    subgraph "File Operations"
        FileReader[file_reader.py<br/>read_data_file<br/>read_csv<br/>read_excel<br/>get_file_columns]
        PDFOps[pdf_operations.py<br/>find_pdf_file<br/>merge_pdfs]
    end
    
    subgraph "Data Processing"
        DataParser[data_parser.py<br/>parse_serial_numbers]
    end
    
    subgraph "Validation"
        Validators[validators.py<br/>validate_file<br/>validate_folder<br/>validate_paths<br/>validate_serial_number]
    end
    
    subgraph "Supporting Modules"
        Logger[logger.py<br/>setup_logger<br/>get_logger]
        Exceptions[exceptions.py<br/>PDFMergerError<br/>FileNotFoundError<br/>InvalidFileFormatError<br/>MissingColumnError<br/>PDFProcessingError<br/>ValidationError]
    end
    
    subgraph "External Libraries"
        PyPDF[pypdf/PyPDF2<br/>PdfReader<br/>PdfWriter]
        Pandas[pandas<br/>Excel Reading]
        CSV[Python csv<br/>CSV Reading]
    end
    
    Main --> CLI
    Main --> Interactive
    CLI --> Processor
    Interactive --> Processor
    
    Processor --> FileReader
    Processor --> PDFOps
    Processor --> DataParser
    Processor --> Logger
    Processor --> Exceptions
    
    FileReader --> CSV
    FileReader --> Pandas
    FileReader --> Exceptions
    FileReader --> Logger
    
    PDFOps --> PyPDF
    PDFOps --> Logger
    
    Validators --> FileReader
    Validators --> Logger
    Validators --> Exceptions
    
    CLI --> Validators
    Interactive --> Validators
    
    style Main fill:#e1f5ff
    style Processor fill:#fff4e1
    style FileReader fill:#f0e1ff
    style PDFOps fill:#ffe1f5
    style Validators fill:#e1ffe1
    style Exceptions fill:#ffe1e1
```

## Exception Hierarchy

```mermaid
classDiagram
    class Exception {
        <<built-in>>
    }
    
    class PDFMergerError {
        +str message
        +__init__(message: str)
    }
    
    class FileNotFoundError {
        +Path path
        +str file_type
        +__init__(path: Path, file_type: str)
    }
    
    class InvalidFileFormatError {
        +Path file_path
        +__init__(message: str, file_path: Path)
    }
    
    class MissingColumnError {
        +str column_name
        +List[str] available_columns
        +Path file_path
        +__init__(column_name: str, available_columns: List[str], file_path: Path)
    }
    
    class PDFProcessingError {
        +Path pdf_path
        +str operation
        +__init__(message: str, pdf_path: Path, operation: str)
    }
    
    class ValidationError {
        +str field
        +__init__(message: str, field: str)
    }
    
    Exception <|-- PDFMergerError
    PDFMergerError <|-- FileNotFoundError
    PDFMergerError <|-- InvalidFileFormatError
    PDFMergerError <|-- MissingColumnError
    PDFMergerError <|-- PDFProcessingError
    PDFMergerError <|-- ValidationError
```

## Processing Flow Sequence

```mermaid
sequenceDiagram
    participant User
    participant Main
    participant CLI/Interactive
    participant Validators
    participant Processor
    participant FileReader
    participant DataParser
    participant PDFOps
    participant Logger
    
    User->>Main: Start Application
    Main->>CLI/Interactive: Route to Mode
    
    alt CLI Mode
        CLI/Interactive->>CLI/Interactive: Parse Arguments
        CLI/Interactive->>Validators: validate_paths()
        Validators->>FileReader: get_file_columns()
        Validators-->>CLI/Interactive: Validation Result
    else Interactive Mode
        CLI/Interactive->>User: Prompt for File Path
        User-->>CLI/Interactive: File Path
        CLI/Interactive->>Validators: validate_file()
        Validators->>FileReader: get_file_columns()
        Validators-->>CLI/Interactive: Validation Result
        CLI/Interactive->>User: Prompt for Source Folder
        User-->>CLI/Interactive: Source Folder
        CLI/Interactive->>Validators: validate_folder()
        Validators-->>CLI/Interactive: Validation Result
    end
    
    CLI/Interactive->>Processor: process_file()
    Processor->>Logger: Log Start Processing
    Processor->>FileReader: read_data_file()
    
    alt CSV File
        FileReader->>FileReader: detect_file_type()
        FileReader->>FileReader: _detect_csv_delimiter()
        FileReader->>FileReader: read_csv()
    else Excel File
        FileReader->>FileReader: detect_file_type()
        FileReader->>FileReader: read_excel() [pandas]
    end
    
    loop For Each Row
        FileReader-->>Processor: Row Dictionary
        Processor->>Processor: process_row()
        Processor->>DataParser: parse_serial_numbers()
        DataParser-->>Processor: List of Filenames
        
        loop For Each Filename
            Processor->>PDFOps: find_pdf_file()
            PDFOps->>PDFOps: Search Source Folder
            PDFOps-->>Processor: PDF Path or None
        end
        
        Processor->>PDFOps: merge_pdfs()
        PDFOps->>PDFOps: Create PdfWriter
        loop For Each PDF
            PDFOps->>PDFOps: Read PDF with PdfReader
            PDFOps->>PDFOps: Add Pages to Writer
        end
        PDFOps->>PDFOps: Write Merged PDF
        PDFOps-->>Processor: Success/Failure
        Processor->>Logger: Log Result
    end
    
    Processor-->>CLI/Interactive: ProcessingResult
    CLI/Interactive->>User: Display Summary
```

## Module Dependencies

```mermaid
graph LR
    subgraph "pdf_merger package"
        A[processor.py] --> B[file_reader.py]
        A --> C[pdf_operations.py]
        A --> D[data_parser.py]
        A --> E[logger.py]
        A --> F[exceptions.py]
        
        B --> F
        B --> E
        
        C --> E
        
        G[validators.py] --> B
        G --> E
        G --> F
        
        H[__init__.py] --> A
        H --> B
        H --> C
        H --> D
        H --> G
        H --> F
    end
    
    subgraph "cli package"
        I[command_line.py] --> H
        I --> G
        I --> E
        
        J[interactive.py] --> H
        J --> G
        J --> E
    end
    
    K[main.py] --> I
    K --> J
    
    style A fill:#fff4e1
    style B fill:#f0e1ff
    style C fill:#ffe1f5
    style G fill:#e1ffe1
    style F fill:#ffe1e1
```
