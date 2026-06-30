import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import './Builder.css';

// Master template definition
const MASTER_TEMPLATE = [
  {
    id: "contact",
    name: "Contact Info",
    icon: "👤",
    fields: [
      { 
        id: "full_name", display: "Full Name", path: "full_name",
        subFields: [
          { id: "first_name", display: "First Name", path: "first_name" },
          { id: "last_name", display: "Last Name", path: "last_name" }
        ]
      },
      { id: "email", display: "Email", path: "emails" },
      { id: "phone", display: "Phone", path: "phones" },
      { 
        id: "location", display: "Location", path: "location",
        isConditional: true,
        subFields: []
      },
      { 
        id: "links", display: "Links", path: "links", isConditional: true,
        subFields: [
          { id: "linkedin", display: "LinkedIn", path: "links.value.linkedin" },
          { id: "github", display: "GitHub", path: "links.value.github" },
          { id: "others", display: "Others", path: "links.value.other" }
        ]
      },
      { id: "current_company", display: "Current Company", path: "current_company", isConditional: true },
      { id: "job_title", display: "Job Title", path: "headline", isConditional: true },
      { id: "years_experience", display: "Years of Experience", path: "years_experience", isConditional: true }
    ]
  },
  {
    id: "education",
    name: "Education",
    icon: "🎓",
    from_array: "education.value",
    fields: [
      { id: "institution", display: "Institution", path: "institution", isDefault: true },
      { id: "degree", display: "Degree", path: "degree", isDefault: true },
      { id: "field", display: "Field of Study", path: "field", isDefault: true },
      { id: "end_year", display: "End Year", path: "end_year", isDefault: true }
    ]
  },
  {
    id: "experience",
    name: "Experience",
    icon: "💼",
    from_array: "experience.value",
    fields: [
      { id: "title", display: "Job Title", path: "title" },
      { id: "company", display: "Company", path: "company" },
      { id: "start", display: "Start Date", path: "start" },
      { id: "end", display: "End Date", path: "end" },
      { id: "summary", display: "Summary", path: "summary" }
    ]
  },
  {
    id: "projects",
    name: "Projects",
    icon: "🚀",
    from_array: "additional_details.value.PROJECTS",
    fields: [
      { id: "title", display: "Title", path: "title" },
      { id: "links", display: "Links", path: "links" }
    ]
  },
  {
    id: "certifications",
    name: "Certifications",
    icon: "🏅",
    from_array: "additional_details.value.CERTIFICATIONS",
    fields: [
      { id: "name", display: "Certificate Name", path: "@" }
    ]
  },
  {
    id: "skills",
    name: "Skills",
    icon: "🛠️",
    fields: [
      {
        id: "primary_skills", display: "Primary Skills", path: "primary_skills.value"
      },
      { id: "secondary_skills", display: "Secondary Skills", path: "secondary_skills.value" }
    ]
  },
  {
    id: "achievements",
    name: "Achievements",
    icon: "🏆",
    from_array: "achievements.value",
    isConditional: true,
    fields: [
      { id: "name", display: "Achievement", path: "name" }
    ]
  },
  {
    id: "additional_details",
    name: "Additional Details",
    icon: "➕",
    from_array: "open_source.value",
    isConditional: true,
    fields: [
      { id: "detail", display: "Open Source Detail", path: "name" }
    ]
  }
];

const PROVENANCE_OPTIONS = [
  { id: 'source', label: 'Source Details', icon: '📄' },
  { id: 'method', label: 'Extraction Method', icon: '⚙️' },
  { id: 'confidence', label: 'Confidence Score', icon: '🎯' },
];

export default function Builder() {
  const location = useLocation();
  const navigate = useNavigate();
  const rawData = location.state?.rawData;

  const [selectedFilters, setSelectedFilters] = useState<string[]>(["source", "method"]);
  const [selectedFields, setSelectedFields] = useState<Record<string, Record<string, boolean>>>({});
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const [expandedFields, setExpandedFields] = useState<Record<string, boolean>>({});
  const [dynamicTemplate, setDynamicTemplate] = useState<any[]>([]);
  const [projectedData, setProjectedData] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [draggedIdx, setDraggedIdx] = useState<number | null>(null);
  const [configCollapsed, setConfigCollapsed] = useState(false);

  // Helper to evaluate path like "emails[0]" or "location.value.city"
  const getValueByPath = (obj: any, path: string) => {
    if (path === "@") return obj;
    try {
      const parts = path.replace(/\[(\d+)\]/g, '.$1').split('.');
      return parts.reduce((acc, part) => (acc && acc[part] !== undefined ? acc[part] : null), obj);
    } catch {
      return null;
    }
  };

  const isValueEmpty = (val: any) => {
    if (val === null || val === undefined) return true;
    if (typeof val === 'object' && val.value === null && (!val.provenance || val.provenance.length === 0)) return true;
    if (Array.isArray(val) && val.length === 0) return true;
    return false;
  };

  // Initialize dynamic template based on conditional data presence
  useEffect(() => {
    if (!rawData) return;
    
    let initialSelections: any = {};
    
    const parsedTemplate = MASTER_TEMPLATE.map(section => {
      // Check section-level conditions
      if (section.isConditional) {
        const arr = section.from_array?.split('.').reduce((o: any, i) => o?.[i], rawData);
        if (!arr || !Array.isArray(arr) || arr.length === 0) return null;
      }

      const validFields = section.fields.map(field => {
        // Check field-level conditions
        if (field.isConditional) {
          const val = getValueByPath(rawData, field.path);
          if (isValueEmpty(val)) return null;
          
          // Special handling for links conditional subfields
          if (field.id === 'links' && val.value) {
            const subFields: any[] = [];
            // For object with named keys (linkedin, github, portfolio) – ignore "other"
            if (typeof val.value === 'object' && !Array.isArray(val.value)) {
              Object.entries(val.value).forEach(([k, v]) => {
                if (k === 'other') return; // Skip generic other links
                if (v && (Array.isArray(v) ? v.length > 0 : true)) {
                  if (Array.isArray(v)) {
                    v.forEach((linkItem: string, idx: number) => {
                      subFields.push({
                        id: `${k}_${idx}` ,
                        display: `${k.charAt(0).toUpperCase() + k.slice(1)} ${idx + 1}` ,
                        path: `links.value.${k}[${idx}]`
                      });
                    });
                  } else {
                    subFields.push({
                      id: k,
                      display: k.charAt(0).toUpperCase() + k.slice(1),
                      path: `links.value.${k}`
                    });
                  }
                }
              });
            }
            field.subFields = subFields.length > 0 ? subFields : undefined;
          }
          
          // Special handling for location conditional subfields
          if (field.id === 'location' && val.value && typeof val.value === 'object') {
             field.subFields = [];
             if (val.value.city) field.subFields.push({ id: "city", display: "City", path: "location.value.city" });
             if (val.value.region) field.subFields.push({ id: "region", display: "Region", path: "location.value.region" });
             if (val.value.country) field.subFields.push({ id: "country", display: "Country", path: "location.value.country" });
             if (field.subFields.length === 0) field.subFields = undefined; // No subfields to show
          }
        }
        
        // Check if main field is empty
        let mainVal: any = null;
        if (section.from_array) {
          const arr = getValueByPath(rawData, section.from_array);
          if (Array.isArray(arr) && arr.some(item => !isValueEmpty(getValueByPath(item, field.path)))) {
            mainVal = "exists"; // Mock non-empty value
          }
        } else {
          mainVal = getValueByPath(rawData, field.path);
        }
        field.isDisabled = isValueEmpty(mainVal) && !field.isClassify;

        // Check if subfields are empty and pre‑select them
        if (field.subFields) {
          field.subFields = field.subFields.map((sub: any) => {
            let subVal: any = null;
            if (section.from_array) {
              const arr = getValueByPath(rawData, section.from_array);
              if (Array.isArray(arr) && arr.some(item => !isValueEmpty(getValueByPath(item, sub.path)))) {
                subVal = "exists";
              }
            } else {
              subVal = getValueByPath(rawData, sub.path);
            }
            sub.isDisabled = isValueEmpty(subVal) && !sub.isClassify;
            // Auto-select subfield if not disabled
            if (!sub.isDisabled) {
              if (!initialSelections[section.id]) initialSelections[section.id] = {};
              initialSelections[section.id][`${field.id}.${sub.id}`] = true;
            }
            return sub;
          });
        }
        
        // Setup initial selections – select all non‑disabled fields by default
        if (!initialSelections[section.id]) initialSelections[section.id] = {};
        // Main field
        if (!field.isDisabled) {
          initialSelections[section.id][field.id] = true;
        }
        // Sub‑fields (if any) – will be filled after subfields are processed below

        return field;
      }).filter(Boolean);
      
      if (validFields.length === 0) return null;
      
      return { ...section, fields: validFields };
    }).filter(Boolean);

    setDynamicTemplate(parsedTemplate);
    setSelectedFields(initialSelections);
  }, [rawData]);

  if (!rawData) {
    return (
      <div className="container flex-col items-center">
        <h2>No extraction data found.</h2>
        <button className="btn btn-primary" onClick={() => navigate('/')}>Go Home</button>
      </div>
    );
  }

  const toggleFilter = (id: string) => {
    setSelectedFilters(prev => prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id]);
  };

  const toggleField = (sectionId: string, fieldId: string, isSubField = false, parentId?: string) => {
    setSelectedFields(prev => {
      const newSec = { ...(prev[sectionId] || {}) };
      
      if (isSubField && parentId) {
        // Toggle subfield state
        const parentState = newSec[parentId] || false;
        if (!parentState) newSec[parentId] = true; // Auto check parent if sub is checked
        newSec[`${parentId}.${fieldId}`] = !newSec[`${parentId}.${fieldId}`];
      } else {
        // Toggle main field state
        newSec[fieldId] = !newSec[fieldId];
        // If unchecking main field, uncheck its subfields
        if (!newSec[fieldId]) {
          Object.keys(newSec).forEach(k => {
            if (k.startsWith(`${fieldId}.`)) newSec[k] = false;
          });
        }
      }
      return { ...prev, [sectionId]: newSec };
    });
  };

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({ ...prev, [sectionId]: !prev[sectionId] }));
  };

  const toggleFieldExpand = (fieldId: string) => {
    setExpandedFields(prev => ({ ...prev, [fieldId]: !prev[fieldId] }));
  };

  const handleDragStart = (e: React.DragEvent, index: number) => {
    setDraggedIdx(index);
    e.dataTransfer.effectAllowed = 'move';
    // Firefox requires some data to be set
    e.dataTransfer.setData('text/html', e.currentTarget.parentNode as any);
  };

  const handleDragOver = (index: number) => {
    if (draggedIdx === null || draggedIdx === index) return;
    
    setDynamicTemplate(prev => {
      const newTemplate = [...prev];
      const draggedItem = newTemplate[draggedIdx];
      newTemplate.splice(draggedIdx, 1);
      newTemplate.splice(index, 0, draggedItem);
      return newTemplate;
    });
    setDraggedIdx(index);
  };

  const handleDragEnd = () => {
    setDraggedIdx(null);
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    
    const buildSubFields = (sectionId: string, parentField: any) => {
      if (!parentField.subFields) return undefined;
      const activeSubs = parentField.subFields.filter((s: any) => selectedFields[sectionId]?.[`${parentField.id}.${s.id}`]);
      if (activeSubs.length === 0) return undefined;
      
      return activeSubs.map((s: any) => ({
        display_name: s.display,
        from: s.path,
        classify_skills: s.isClassify || false
      }));
    };

    const sectionsConfig = dynamicTemplate
      .filter(sec => Object.keys(selectedFields[sec.id] || {}).some(k => !k.includes('.') && selectedFields[sec.id][k]))
      .map(sec => ({
        section_name: sec.name,
        from_array: sec.from_array,
        fields: sec.fields
          .filter((f: any) => selectedFields[sec.id]?.[f.id])
          .map((f: any) => ({
            display_name: f.display,
            from: f.path,
            sub_fields: buildSubFields(sec.id, f)
          }))
      }));

    const config = {
      provenance_filters: selectedFilters,
      sections: sectionsConfig
    };

    try {
      const res = await fetch('http://127.0.0.1:8000/api/extract/project', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: rawData, config })
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const result = await res.json();
      setProjectedData(result);
      setConfigCollapsed(true); // Auto-collapse config panel after generation
    } catch (err) {
      console.error(err);
      alert("Failed to generate projection.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="builder-page">
      <div className="builder-header glass-panel flex items-center justify-between">
        <h1 className="header-title">Resume Builder</h1>
        <button className="btn btn-primary" onClick={handleGenerate} disabled={isGenerating}>
          {isGenerating ? 'Generating...' : 'Generate Profile'}
        </button>
      </div>

      <Sidebar>
        <div className="sidebar-section">
          <div className="section-subtitle">FILTERS</div>
          <div className="filters-menu">
            {PROVENANCE_OPTIONS.map(opt => (
              <label key={opt.id} className="filter-checkbox-label">
                <input type="checkbox" checked={selectedFilters.includes(opt.id)} onChange={() => toggleFilter(opt.id)}/>
                <div className="checkbox-custom"></div>
                <span className="filter-text">
                  {opt.icon && <span className="filter-icon" style={{ marginRight: '6px' }}>{opt.icon}</span>}
                  {opt.label}
                </span>
              </label>
            ))}
          </div>
        </div>
      </Sidebar>

      <div className={`builder-content flex ${configCollapsed ? 'config-hidden' : ''}`}>
        <div className="preview-panel glass-panel">
          <h2>Projected Profile Preview</h2>
          {projectedData ? (
            <div className="preview-tree">
              {projectedData.sections.map((sec: any, idx: number) => {
                const secId = sec.section_name?.toLowerCase().replace(/\s+/g, '_') || '';
                const themeMap: Record<string,string> = {
                  'contact_info': 'contact', 'contact': 'contact',
                  'experience': 'experience', 'education': 'education',
                  'projects': 'projects', 'certifications': 'certifications',
                  'skills': 'skills', 'achievements': 'achievements',
                  'additional_details': 'additional_details',
                };
                const sectionTheme = themeMap[secId] || secId;
                
                // Try to find the root provenance for array-based sections
                const templateSec = MASTER_TEMPLATE.find(t => t.name === sec.section_name);
                let secProv: any[] | undefined = undefined;
                if (templateSec && templateSec.from_array) {
                  const rootKey = templateSec.from_array.split('.')[0];
                  if (rawData[rootKey] && rawData[rootKey].provenance) {
                    // Filter it based on selected filters, just like backend does
                    secProv = rawData[rootKey].provenance.map((p: any) => {
                      const filtered: any = {};
                      selectedFilters.forEach(f => {
                        if (f in p) filtered[f] = p[f];
                      });
                      
                      // Simulate confidence if requested
                      if (selectedFilters.includes('confidence') && !('confidence' in filtered)) {
                        const sourceStr = String(p.source || '');
                        filtered.confidence = sourceStr.toLowerCase().endsWith('.csv') ? 1.0 : 0.85;
                      }
                      
                      return Object.keys(filtered).length > 0 ? filtered : null;
                    }).filter(Boolean);
                  }
                }

                return (
                  <div key={idx} className="preview-section" data-section={sectionTheme}>
                    <h3>
                      {templateSec?.icon && <span className="section-icon" style={{ marginRight: '8px' }}>{templateSec.icon}</span>}
                      {sec.section_name}
                    </h3>
                    {Array.isArray(sec.data) ? (
                      sec.data.map((item: any, i: number) => (
                        <div key={i} className="preview-item-group">
                          <RecursivePreview data={item} sectionHint={sectionTheme} inheritedProvenance={secProv} />
                        </div>
                      ))
                    ) : (
                      <div className="preview-item-group">
                        <RecursivePreview data={sec.data || {}} sectionHint={sectionTheme} inheritedProvenance={secProv} />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="empty-state">Configure your template and click Generate.</div>
          )}
        </div>

        {/* ─── Pull tab toggle ─── */}
        <button
          className={`config-pull-tab ${configCollapsed ? 'collapsed' : ''}`}
          onClick={() => setConfigCollapsed(prev => !prev)}
          title={configCollapsed ? 'Show Configuration' : 'Hide Configuration'}
        >
          <span className="pull-tab-icon">{configCollapsed ? '◀' : '▶'}</span>
          {configCollapsed && <span className="pull-tab-label">Config</span>}
        </button>

        <div className={`config-panel glass-panel ${configCollapsed ? 'panel-collapsed' : ''}`}>
          <h2>Configuration</h2>
          <div className="sections-list">
            {dynamicTemplate.map((section, idx) => (
              <div 
                key={section.id} 
                className={`config-section ${expandedSections[section.id] ? 'is-expanded' : ''}`}
                draggable
                onDragStart={(e) => handleDragStart(e, idx)}
                onDragOver={(e) => { e.preventDefault(); handleDragOver(idx); }}
                onDragEnd={handleDragEnd}
                style={{ opacity: draggedIdx === idx ? 0.5 : 1 }}
              >
                <h3 className="collapsible-header section-header">
                  <div className="section-title-wrap" onClick={() => toggleSection(section.id)}>
                    <span className="toggle-icon">{expandedSections[section.id] ? '▼' : '▶'}</span>
                    {section.icon && <span className="section-icon" style={{ marginRight: '8px' }}>{section.icon}</span>}
                    {section.name}
                  </div>
                  <span className="drag-handle" title="Drag to reorder">⠿</span>
                </h3>
                
                {expandedSections[section.id] && (
                  <div className="fields-list">
                    {section.fields.map((field: any) => (
                      <div key={field.id} className="field-group">
                        <div className="field-row-header">
                          {field.subFields ? (
                            <span 
                              className="toggle-icon field-toggle" 
                              onClick={() => toggleFieldExpand(field.id)}
                            >
                              {expandedFields[field.id] ? '▼' : '▶'}
                            </span>
                          ) : (
                            <span className="toggle-spacer"></span>
                          )}
                          <label 
                            className={`checkbox-label field-cb ${field.isDisabled ? 'disabled' : ''}`}
                            title={field.isDisabled ? "Null value" : ""}
                          >
                            <input 
                              type="checkbox" 
                              checked={selectedFields[section.id]?.[field.id] || false}
                              onChange={() => toggleField(section.id, field.id)}
                              disabled={field.isDisabled}
                            />
                            {field.display}
                          </label>
                        </div>
                        
                        {field.subFields && expandedFields[field.id] && (
                          <div className="subfields-list">
                            {field.subFields.map((sub: any) => (
                              <label 
                                key={sub.id} 
                                className={`checkbox-label sub-cb ${sub.isDisabled ? 'disabled' : ''}`}
                                title={sub.isDisabled ? "Null value" : ""}
                              >
                                <input 
                                  type="checkbox" 
                                  checked={selectedFields[section.id]?.[`${field.id}.${sub.id}`] || false}
                                  onChange={() => toggleField(section.id, sub.id, true, field.id)}
                                  disabled={sub.isDisabled}
                                />
                                {sub.display}
                              </label>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════
// HELPER UTILITIES
// ═══════════════════════════════════════════════

// Clean a string value — strip "(Certificate)", "[LINK:...]", and similar artefacts
function cleanDisplayValue(val: string): string {
  return val
    .replace(/\s*\(Certificate\)/gi, '')
    .replace(/\[LINK:.*?\]/gi, '')
    .trim();
}

// Check if a value is effectively null
function isDisplayNull(val: any): boolean {
  if (val === null || val === undefined || val === 'null' || val === '') return true;
  if (Array.isArray(val) && val.length === 0) return true;
  if (typeof val === 'object' && Object.keys(val).length === 0) return true;
  return false;
}

// Render a NULL badge
function renderNull() {
  return <span className="null-badge">NULL</span>;
}

// Detect URLs
function isUrl(s: string): boolean {
  return /^https?:\/\//i.test(s);
}

// Heuristic: is the string "long" (summaries, descriptions)?
function isLongText(s: string): boolean {
  return s.length > 80;
}

// Keys that hint "this field is a skills-like array"
const SKILLS_KEYS = new Set(['primary_skills', 'secondary_skills', 'primary skills', 'secondary skills', 'skills', 'tools', 'technologies']);

// ═══════════════════════════════════════════════
// RecursivePreview
// ═══════════════════════════════════════════════
function RecursivePreview({ data, depth = 0, sectionHint = '', fieldKey = '', inheritedProvenance }: {
  data: any;
  depth?: number;
  sectionHint?: string;
  fieldKey?: string;
  inheritedProvenance?: any[];
}) {
  if (isDisplayNull(data)) return renderNull();

  // ── Primitive value ──
  if (typeof data !== 'object') {
    const str = cleanDisplayValue(String(data));
    if (!str || str === 'null') return renderNull();

    // Render URLs as clickable links
    if (isUrl(str)) {
      return (
        <a className="link-item" href={str} target="_blank" rel="noopener noreferrer">
          <span className="link-icon">🔗</span>{str}
        </a>
      );
    }

    // Long text gets its own class to span full width
    if (isLongText(str)) {
      return <span className="long-text">{str}</span>;
    }

    return <span className="field-value">{str}</span>;
  }

  // ── Plain array ──
  if (Array.isArray(data)) {
    if (data.length === 0) return renderNull();

    // Array of primitives
    if (data.every(item => typeof item !== 'object')) {
      const cleaned = data
        .map(item => cleanDisplayValue(String(item)))
        .filter(v => v && v !== 'null');
      const unique = Array.from(new Set(cleaned));
      if (unique.length === 0) return renderNull();

      // If every item is a URL → render as link list, limit to 3 if "links" or "others" context
      if (unique.every(isUrl)) {
        const displayLinks = unique.slice(0, 3);
        const hasMore = unique.length > 3;
        return (
          <div className="link-list">
            {displayLinks.map((url, i) => (
              <a key={i} className="link-item" href={url} target="_blank" rel="noopener noreferrer">
                <span className="link-icon">🔗</span>{url}
              </a>
            ))}
            {hasMore && <span className="link-more-text">+{unique.length - 3} more</span>}
          </div>
        );
      }

      // If this is a skills-like field → render as chips
      const lowerKey = fieldKey.toLowerCase().replace(/[^a-z_]/g, '');
      if (sectionHint === 'skills' || SKILLS_KEYS.has(lowerKey)) {
        return (
          <div className="skill-chips">
            {unique.map((s, i) => (
              <span key={i} className="skill-chip">{s}</span>
            ))}
          </div>
        );
      }

      // Default: comma-separated
      return <span className="field-value comma-list">{unique.join(', ')}</span>;
    }

    // Array of objects → numbered 1-based list
    return (
      <div className="array-items-list">
        {data.map((item, i) => (
          <div key={i} className="array-item-row">
            <span className="array-index">{i + 1}.</span>
            <div className="array-item-content">
              <RecursivePreview data={item} depth={depth + 1} sectionHint={sectionHint} inheritedProvenance={inheritedProvenance} />
            </div>
          </div>
        ))}
      </div>
    );
  }

  // ── Wrapper object with "value" + "provenance" ──
  if (data && typeof data === 'object' && 'value' in data && 'provenance' in data) {
    const subKeys = Object.keys(data).filter(k => k !== 'value' && k !== 'provenance');
    const val = data.value;
    const currentProv = (data.provenance && data.provenance.length > 0) ? data.provenance : inheritedProvenance;
    
    if (isDisplayNull(val) && subKeys.length === 0) return renderNull();

    return (
      <div className="preview-field-wrapper">
        <div className="preview-field flex items-center">
          <span className="field-value">
            {typeof val === 'object' && val !== null ? (
              Array.isArray(val) ? (
                // Array inside value wrapper
                <RecursivePreview data={val} depth={depth + 1} sectionHint={sectionHint} fieldKey={fieldKey} inheritedProvenance={currentProv} />
              ) : (
                // Nested object (location, classified skills, etc.)
                <div className="nested-raw-object">
                  {Object.entries(val).map(([k, v]) => {
                    return (
                      <div key={k} className="classified-category">
                        <strong>{k}:</strong>{' '}
                        {isDisplayNull(v) ? renderNull() : (
                          Array.isArray(v)
                            ? Array.from(new Set((v as any[]).map(x => cleanDisplayValue(String(x))).filter(x => x && x !== 'null'))).join(', ')
                            : cleanDisplayValue(String(v))
                        )}
                      </div>
                    );
                  })}
                </div>
              )
            ) : (
              (() => {
                const s = cleanDisplayValue(String(val));
                if (!s || s === 'null') return renderNull();
                if (isUrl(s)) return <a className="link-item" href={s} target="_blank" rel="noopener noreferrer"><span className="link-icon">🔗</span>{s}</a>;
                if (isLongText(s)) return <span className="long-text">{s}</span>;
                return s;
              })()
            )}
          </span>
          {currentProv && currentProv.length > 0 && (
            <div className="tooltip-container">
              <span className="source-icon">ℹ️</span>
              <div className="tooltip-content glass-panel">
                {currentProv.map((prov: any, i: number) => {
                  return (
                    <div key={i} className="prov-item">
                      <div className="prov-header">Source Details</div>
                      { 'source' in prov && (
                        <>
                          <div className="prov-line"><strong>Title:</strong> {prov.source}</div>
                          <div className="prov-line"><strong>Type:</strong> {String(prov.source).toLowerCase().endsWith('.csv') ? 'Structured (CSV)' : 'Unstructured (Document)'}</div>
                        </>
                      )}
                      { 'method' in prov && (
                        <div className="prov-line"><strong>Method:</strong> {prov.method}</div>
                      )}
                      { 'raw_value' in prov && (
                        <div className="prov-line"><strong>Raw Value:</strong> {String(prov.raw_value)}</div>
                      )}
                      { 'confidence' in prov && (
                        <div className="prov-line"><strong>Confidence:</strong> <span className="conf-badge">{typeof prov.confidence === 'number' ? (prov.confidence * 100).toFixed(1) : prov.confidence}%</span></div>
                      )}
                      { Object.keys(prov).length === 0 && (
                        <div className="prov-line" style={{ color: '#94a3b8' }}>No source details available or selected.</div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {subKeys.length > 0 && (
          <div className="sub-fields-container">
            {subKeys.map(key => (
              <div key={key} className="sub-field-row">
                <span className="field-label sub-label">{key}:</span>
                <RecursivePreview data={data[key]} depth={depth + 1} sectionHint={sectionHint} fieldKey={key} inheritedProvenance={currentProv} />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  // ── Plain object (dict) ──
  const entries = Object.entries(data);
  if (entries.length === 0) return renderNull();

  return (
    <div className={`dict-grid ${sectionHint === 'certifications' ? 'cert-grid' : ''} ${sectionHint === 'contact' ? 'contact-grid' : ''}`}>
      {entries.map(([key, val]: [string, any]) => {
        const isNull = typeof val === 'string' && cleanDisplayValue(val) === 'null';
        const displayVal = isNull ? null : val;
        return (
          <div key={key} className="dict-row">
            <span className="field-label main-label">{key}:</span>
            <div className="dict-val">
              <RecursivePreview data={displayVal} depth={depth + 1} sectionHint={sectionHint} fieldKey={key} inheritedProvenance={inheritedProvenance} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
