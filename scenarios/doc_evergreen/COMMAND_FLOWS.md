# doc-evergreen Command Flows

## Create Command Flow

```mermaid
flowchart TD
    Start([User runs create command<br/>Inputs: CLI args]) --> Validate{Validate parameters<br/>Inputs: --about, --output}
    Validate -->|Missing required| Error1[Error: Missing --about or --output]
    Validate -->|Valid| FindRoot[Find git repository root<br/>Input: current working directory]

    FindRoot --> CheckCwd{Current directory<br/>is git root?}
    CheckCwd -->|No| Warn[Warn user + confirm]
    CheckCwd -->|Yes| DiscoverFiles
    Warn --> DiscoverFiles

    DiscoverFiles{Sources specified?<br/>Input: --sources flag}
    DiscoverFiles -->|Yes| GatherExplicit[Gather files matching patterns<br/>Input: --sources patterns<br/>Supports: exact files + globs]
    DiscoverFiles -->|No| LLMDiscovery[LLM-guided discovery<br/>Inputs: --about + repo structure]

    GatherExplicit --> CheckSize[Estimate total file size<br/>Input: gathered file contents]
    LLMDiscovery --> CheckSize

    CheckSize --> DryRun{Dry run mode?<br/>Input: --dry-run flag}
    DryRun -->|Yes| ShowPreview[Show what would be done]
    DryRun -->|No| SelectTemplate
    ShowPreview --> End([End])

    SelectTemplate{Template specified?<br/>Input: --template flag}
    SelectTemplate -->|Yes| LoadSpecified[Load specified template<br/>Input: template name]
    SelectTemplate -->|No| LLMSelect[LLM selects template<br/>Inputs: --about + repo context]

    LoadSpecified --> DecideCustom{Customization flag?<br/>Inputs: --customize-template<br/>or --no-customize-template}
    LLMSelect --> DecideCustom

    DecideCustom -->|--customize-template| CustomizeForced[Customize template<br/>Inputs: template + sources + about]
    DecideCustom -->|--no-customize-template| UseDirectly[Use template directly]
    DecideCustom -->|No flag provided| AskLLM{LLM evaluates<br/>Inputs: template + sources up to 10KB + about<br/>Analyzes: architecture, CLI commands, APIs}

    AskLLM -->|YES + reason| CustomizeLLM[Customize template<br/>Inputs: template + sources + about]
    AskLLM -->|NO + reason| UseDirectlyLLM[Use template directly]

    UseDirectly --> Generate
    UseDirectlyLLM --> Generate
    CustomizeForced --> SaveTemplate1[Save customized template<br/>to .doc-evergreen/templates/]
    CustomizeLLM --> SaveTemplate2[Save customized template<br/>to .doc-evergreen/templates/]

    SaveTemplate1 --> Generate
    SaveTemplate2 --> Generate

    Generate[Generate documentation via LLM<br/>Inputs: final template + all sources + about]

    Generate --> CheckExisting{Output file exists?<br/>Input: --output path}
    CheckExisting -->|Yes| Backup[Backup to<br/>.doc-evergreen/versions/<br/>Input: existing file]
    CheckExisting -->|No| Save
    Backup --> Save[Save generated document<br/>Input: generated content]

    Save --> UpdateHistory[Update history.yaml<br/>Inputs: sources, template, timestamp]
    UpdateHistory --> Success[✓ Document created successfully]
    Success --> End
```

## Regenerate Command Flow

```mermaid
flowchart TD
    Start([User runs regenerate command<br/>Inputs: CLI args]) --> ValidateArgs{Validate arguments<br/>Inputs: doc path, --all flag}

    ValidateArgs -->|No doc path<br/>and no --all| Error1[Error: Must specify<br/>doc path or --all]
    ValidateArgs -->|Both specified| Error2[Error: Cannot specify<br/>both doc path and --all]
    ValidateArgs -->|Valid| FindRoot[Find git repository root<br/>Input: current working directory]

    FindRoot --> LoadHistory[Load .doc-evergreen/history.yaml<br/>Input: repo root path]

    LoadHistory --> CheckHistory{History exists?<br/>Input: history.yaml file}
    CheckHistory -->|No| Error3[Error: No history found<br/>Run create command first]
    CheckHistory -->|Yes| Mode{Regenerate mode?<br/>Input: CLI arguments}

    Mode -->|Single doc| GetSingleConfig[Get config for specified document<br/>Input: doc path from CLI]
    Mode -->|All docs| GetAllConfigs[Get configs for all documents<br/>Input: all docs in history]

    GetSingleConfig --> CheckConfig{Config exists?<br/>Input: doc key in history}
    CheckConfig -->|No| Error4[Error: Document not in history]
    CheckConfig -->|Yes| ProcessSingle[Process single document]

    GetAllConfigs --> CheckEmpty{Any docs in history?<br/>Input: docs section of history}
    CheckEmpty -->|No| Error5[Error: No documents to regenerate]
    CheckEmpty -->|Yes| ProcessAll[Process each document]

    ProcessSingle --> RegenerateDoc
    ProcessAll --> RegenerateDoc

    RegenerateDoc[For each document:<br/>Input: doc config from history]
    RegenerateDoc --> LoadConfig[Load saved config<br/>Inputs: sources patterns,<br/>template name, about description]

    LoadConfig --> GatherSources[Gather files matching patterns<br/>Inputs: saved source patterns + repo]

    GatherSources --> DryRun{Dry run mode?<br/>Input: --dry-run flag}
    DryRun -->|Yes| ShowPreview[Show what would be done]
    DryRun -->|No| LoadTemplate
    ShowPreview --> CheckMore{More docs to process?}

    LoadTemplate{Customized template exists?<br/>Input: template_path from history}
    LoadTemplate -->|Yes| LoadCustom[Load customized template<br/>Input: .doc-evergreen/templates/ path]
    LoadTemplate -->|No| LoadBuiltin[Load built-in template<br/>Input: template name]

    LoadCustom --> Generate
    LoadBuiltin --> Generate

    Generate[Generate documentation via LLM<br/>Inputs: template + sources + about]

    Generate --> Backup[Backup existing document<br/>Inputs: current doc content,<br/>.doc-evergreen/versions/ path]

    Backup --> Save[Save generated document<br/>Inputs: generated content, output path]

    Save --> AddVersion[Add version entry to history<br/>Inputs: timestamp, backup path,<br/>template used, sources used]

    AddVersion --> Success[✓ Document regenerated]

    Success --> CheckMore
    CheckMore -->|Yes| RegenerateDoc
    CheckMore -->|No| End([End])

    Error3 --> End
    Error4 --> End
    Error5 --> End
```

## Template Customization Decision Tree

```mermaid
flowchart TD
    Start([Template Selection Complete]) --> CheckFlag{Check CLI flag:<br/>--customize-template?<br/>--no-customize-template?}

    CheckFlag -->|Flag: --customize-template| ForceCustomize[Scenario 1:<br/>✓ Always customize<br/>User explicitly requested]
    CheckFlag -->|Flag: --no-customize-template| ForceSkip[Scenario 2:<br/>✓ Never customize<br/>User explicitly requested]
    CheckFlag -->|No flag provided| AskLLM{Scenario 3:<br/>Ask LLM to evaluate<br/>Inputs: sources + template + about}

    AskLLM -->|LLM analyzes:<br/>• Source file patterns up to 10KB<br/>• Template structure<br/>• Project architecture<br/>• CLI commands/APIs<br/>• Config options| Decision{LLM<br/>decision}

    Decision -->|YES + reason<br/>Example: Project has CLI<br/>commands needing section| CustomizeLLM[✓ Customize template]

    Decision -->|NO + reason<br/>Example: Template structure<br/>already sufficient| UseDirectlyLLM[✓ Use template directly]

    ForceCustomize --> Customize[Perform Customization:<br/>Inputs: sources + template + about<br/>• LLM analyzes code patterns<br/>• Adds project-specific sections<br/>• Adjusts tone for audience<br/>• Saves to .doc-evergreen/templates/]

    CustomizeLLM --> Customize

    ForceSkip --> UseDirectly[Use Template Directly:<br/>• No modification<br/>• No saved custom template<br/>• Uses built-in as-is]

    UseDirectlyLLM --> UseDirectly

    Customize --> Generate([Generate Documentation<br/>Inputs: final template + all sources + about])
    UseDirectly --> Generate
```

## Customization Scenarios Summary

### Scenario 1: Template Specified → Use Directly
```bash
doc-evergreen create \
    --about "API documentation" \
    --output docs/API.md \
    --template api-reference
# Result: Uses api-reference template as-is
```

### Scenario 2: Template Specified + Force Customize
```bash
doc-evergreen create \
    --about "API documentation" \
    --output docs/API.md \
    --template api-reference \
    --customize-template
# Result: Customizes api-reference based on source code
```

### Scenario 3: LLM-Selected → LLM Decides Not Needed
```bash
doc-evergreen create \
    --about "Simple README" \
    --output README.md
# LLM selects: readme template
# LLM evaluates: "NO: Template structure sufficient"
# Result: Uses readme template as-is
```

### Scenario 4: LLM-Selected → LLM Decides Customization Needed
```bash
doc-evergreen create \
    --about "CLI tool documentation" \
    --output README.md
# LLM selects: readme template
# LLM evaluates: "YES: CLI command structure needs dedicated section"
# Result: Customizes readme template to add CLI commands section
```

## File Structure After Operations

```
.doc-evergreen/
├── history.yaml              # All document configurations and versions
├── templates/
│   ├── readme-custom.v1.md  # Customized templates (if created)
│   └── api-reference-custom.v1.md
└── versions/
    ├── README.md.2025-01-07T10-30-00.bak
    └── docs/API.md.2025-01-07T11-15-00.bak
```

## Key Decision Points

### Source Discovery
- **With `--sources`**: Use exact files + glob patterns
- **Without `--sources`**: LLM-guided breadth-first discovery

### Template Selection
- **With `--template`**: Use specified template
- **Without `--template`**: LLM selects based on `--about`

### Template Customization
- **`--customize-template`**: Always customize
- **`--no-customize-template`**: Never customize
- **No flag + template specified**: Use directly
- **No flag + LLM-selected**: Ask LLM if beneficial
