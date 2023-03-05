import { h } from 'preact'
import { useState, useEffect, useRef, useLayoutEffect } from 'preact/hooks'
import { getTranslation, localizationKeys } from 'src/util/localization'
import { deleteAPI, getDefaultAPI, getsavedAPIs, API, saveAPI } from 'src/util/apiManager'
const APIEditor = (
) => {
    const [savedAPIS, setSavedAPIS] = useState<API[]>([])
    const [api, setAPI] = useState<API>(getDefaultAPI())
    const [deleteBtnText, setDeleteBtnText] = useState("delete")
    const [showErrors, setShowErrors] = useState(false)
    const [nameError, setNameError] = useState(false)
    const [textError, setTextError] = useState(false)

    useLayoutEffect(() => {
        updateSavedAPIS()
    }, [])

    const updateSavedAPIS = async () => {
        const apis = await getsavedAPIs()
        setSavedAPIS(apis)
        if (api.uuid === 'default') {
            setAPI(apis[0])
        }
    }

    useEffect(() => {
        setNameError(api.name.trim() === '')
        setTextError(api.text.trim() === '')
    }, [api])

    async function updateList() {
        getsavedAPIs().then(sp => {
            setSavedAPIS(sp)
        })
    }

    const handleSelect = (api:API) => {
        setShowErrors(false)
        setAPI(api)
        setDeleteBtnText("delete")
    }

    const handleAdd = () => {
        setShowErrors(false)
        setAPI({ name: '', text: '' })
        setDeleteBtnText("delete")
        if (nameInputRef.current) {
            nameInputRef.current.focus()
        }
    }

    const handleSave = async () => {
        setShowErrors(true)
        if (nameError || textError) {
            return
        }
        await saveAPI(api)
        await updateList()
    }

    const handleDeleteBtnClick = () => {
        if (deleteBtnText === "delete") {
            setDeleteBtnText("check")
        } else {
            handleDelete()
        }
    }

    const handleDelete = async () => {
        await deleteAPI(api)
        updateList()
        handleAdd()
    }

    const nameInputRef = useRef<HTMLInputElement>(null)
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const handleTextareaChange = (e: Event) => {
        const text = (e.target as HTMLTextAreaElement).value
        if (text !== api.text) {
            setTextError(false)
            setAPI({ ...api, text })
        }
    }
    const actionToolbar = (
        <div className={`wcg-mt-4 wcg-flex wcg-flex-row wcg-justify-between
                        ${api.uuid === 'default' }`}
        >
            <button
                className="wcg-btn-primary wcg-btn wcg-text-base"
                onClick={handleSave}
            >
                {getTranslation(localizationKeys.buttons.save)}
            </button>
        </div >
    )

    const APIList = (
        <div>
            <button
                className="wcg-btn-primary wcg-btn wcg-w-full wcg-text-base"
                onClick={handleAdd}>
                <span class="material-symbols-outlined wcg-mr-2">
                    add_circle
                </span>
                "New API"
            </button>
            <ul className="wcg-scroll-y wcg-menu wcg-mt-4 wcg-flex wcg-max-h-96 wcg-scroll-m-0 wcg-flex-col
                    wcg-flex-nowrap wcg-overflow-auto wcg-border-2
                    wcg-border-solid wcg-border-white/20 wcg-p-0">
                {savedAPIS.map((apii:API) => (
                    <li
                        key={apii.uuid}
                        onClick={() => handleSelect(apii)}
                    >
                        <a className={`wcg-text-base ${apii.uuid === api.uuid ? 'wcg-active' : ''}`}>
                            📝 {apii.name}
                        </a>
                    </li>
                ))}
            </ul>
        </div>
    )

    const nameInput = (
        <input
            ref={nameInputRef}
            className={`wcg-input-bordered wcg-input wcg-flex-1
                        ${showErrors && nameError ? "wcg-input-error" : ""}`
            }
            placeholder={getTranslation(localizationKeys.placeholders.namePlaceholder)}
            value={api.name}
            onInput={(e: Event) => {
                setNameError(false)
                setAPI({ ...api, name: (e.target as HTMLInputElement).value })
            }}
            disabled={api.uuid === 'default'}
        />
    )

    const btnDelete = (
        <button
            className={`wcg-btn wcg-text-base
                    ${deleteBtnText === "check" ? "wcg-btn-error" : "wcg-btn-primary"}
                    ${api.uuid === 'default'}`}
            onClick={handleDeleteBtnClick}
        >
            <span class="material-symbols-outlined">
                {deleteBtnText}
            </span>
        </button>
    )

    const textArea = (
        <textarea
            ref={textareaRef}
            className={`wcg-textarea-bordered wcg-textarea
                        ${showErrors && textError ? "wcg-textarea-error" : ""}
                        wcg-mt-2 wcg-h-96 wcg-resize-none wcg-text-base`}
            value={api.text}
            onInput={handleTextareaChange}
            disabled={api.uuid === 'default'}
        />
    )

    return (
        <div className="wcg-rounded-box wcg-mt-10 wcg-flex wcg-h-[32rem] wcg-w-4/5 wcg-flex-row wcg-gap-4 wcg-border wcg-py-4">
            <div className="wcg-w-1/3">
                {APIList}
            </div>

            <div className="wcg-flex wcg-w-2/3 wcg-flex-col">
                <div className="wcg-flex wcg-flex-row wcg-items-center wcg-gap-2">
                    {nameInput}
                    {btnDelete}
                </div>
                {textArea}

                {actionToolbar}
            </div>
        </div >
    )
}

export default APIEditor
