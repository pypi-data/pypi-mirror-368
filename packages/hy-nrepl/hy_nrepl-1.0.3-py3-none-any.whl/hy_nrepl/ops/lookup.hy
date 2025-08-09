(import sys inspect logging re)
(import pathlib [Path])
(import hy.models [Symbol])
(import hy.reader.mangling [mangle])
(import hy-nrepl.ops.utils [ops])
(require hy-nrepl.ops.utils [defop])
(import toolz [first second nth])

(defn resolve-module [sym]
  (setv m (re.match r"(\S+(\.[\w-]+)*)\.([\w-]*)$" sym))
  (setv groups (.group m 1 3))
  groups)

(defn split-string-by-first-dot [input-string]
  (input-string.split "." 1))

(defn contain-dot? [input-string]
  (in "." input-string))

(defn %resolve-symbol [m sym]
  (if (contain-dot? sym)
      (let [parts (split-string-by-first-dot sym)
            result (eval (Symbol (mangle (get parts 0))) (. m __dict__))]
        (logging.debug "%%resolve-symbol: parts= %s, result= %s" parts result)
        (if (inspect.ismodule result)
            (%resolve-symbol result (get parts 1))
            (eval (mangle sym) (. m __dict__))))
      (eval (Symbol (mangle sym)) (. m __dict__))))

(defn resolve-symbol [m sym]
  (try
    ;; Find from variables or functions
    (%resolve-symbol m sym)
    ;; If not found, then find from macros
    (except [e NameError]
      (try
        (get _hy_macros (mangle sym))
        (except [e KeyError]
          None)))
    (except [e SyntaxError] None)
    (except [e ValueError] None)
    (except [e AssertionError] None)
    (except [e AttributeError] None)))

(defn find-pattern [pattern file-path]
  (with [f (open file-path 'r)]
    (for [[i line] (enumerate (f.readlines) :start 1)]
      (when (re.search pattern line)
        (return i)))
    None))

(defn find-class-definition [obj file-path [lang "hylang"]]
  (cond (= lang "hylang")
        (let [pattern r"^\s*\(\s*defclass\s+{}"]
          (find-pattern (.format pattern obj.__name__) file-path))

        (= lang "python")
        (try
          (second (inspect.getsourcelines obj))
          (except [e OSError]
            None))

        :else (raise (ValueError "Unknown lang"))))

(defn get-source-details [x]
  "Get line number, source file of x."
  (let [raw-file (inspect.getsourcefile x)
        path (if (and raw-file
                      (isinstance raw-file str)
                      (> (len raw-file) 0)
                      ;; Add check to exclude '<...>' style names
                      (not (and (.startswith raw-file "<")
                                (.endswith raw-file ">"))))
                 (Path raw-file)
                 (return {}))
        uri (.as_uri (.resolve path)) ; Ensure absolute path
        file (if (.startswith uri "file:///")
                 (.replace uri "file:///" "file:/" 1) ; Substitution only the first time
                 uri)
        module (if (inspect.ismodule x)
                   x.__name__
                   x.__module__)
        ext (cut file -3 None)
        lang (match ext
                    ".py" "python"
                    ".hy" "hylang")
        lnum (cond
               ;; function or method
               (and (hasattr x "__code__")
                    (hasattr x.__code__ "co_firstlineno"))
               x.__code__.co-firstlineno

               ;; class
               (inspect.isclass x)
               (or (find-class-definition x path :lang lang)
                   1)

               ;; other
               :else
               1)]
    {"line" lnum
     "ns" module
     "file" file
     "language" lang
     "extension" ext}))

(defn get-info [session symbol-name]
  (let [symbol (resolve-symbol session.module symbol-name)
        doc (inspect.getdoc symbol)
        sig (try
              (and (callable symbol) (inspect.signature symbol))
              (except [e ValueError]
                None))
        result {}]
    (logging.debug "get-info: Got object %s for symbol %s, session.module: %s"
                   symbol symbol-name session.module)
    (when (is-not symbol None)
      (.update result
               {"doc" (or doc "No doc string")
                "static" "true"
                "name" symbol-name})
      ;; get definition position
      (try
        (.update result (get-source-details symbol))
        (except [e TypeError]))
      (when sig
        (.update result {"arglists-str" (str sig)})))
    result))

(defop lookup [session msg transport]
  {"doc" "Lookup symbol info"
   "requires" {"sym" "The symbol to look up"}
   "returns" {"info" "A map of the symbol’s info."
              "status" "done"}}
  (logging.debug "lookup: msg=%s" msg)
  (let [info (get-info session (.get msg "sym"))]
    (.write session
            {"info" info
             "id" (.get msg "id")
             "status" ["done"]}
            transport)))
