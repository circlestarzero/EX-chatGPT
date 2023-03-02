import "../style/base.css"
import { h, render } from "preact"
import { getUserConfig, updateUserConfig } from "src/util/userConfig"
import { useLayoutEffect, useState } from "preact/hooks"
import PromptEditor from "src/components/promptEditor"
import { getTranslation, localizationKeys, setLocaleLanguage } from "src/util/localization"
import NavBar from "src/components/navBar"
import APIEditor from "src/components/apiEditor"
// const SocialCard = ({ icon, text }: { icon: JSX.Element, text: string }) => (
//     <div className="wcg-btn wcg-btn-ghost wcg-h-28 wcg-w-36 wcg-p-2 wcg-rounded-xl wcg-flex wcg-flex-col">
//         {icon}`
//         <p className="wcg-normal-case wcg-p-2">{text}</p>
//     </div>
// )


export default function OptionsPage() {

    const [language, setLanguage] = useState<string>(null)


    useLayoutEffect(() => {
        getUserConfig().then(config => {
            setLanguage(config.language)
            setLocaleLanguage(config.language)
        })
    }, [])

    const onLanguageChange = (language: string) => {
        setLanguage(language)
        updateUserConfig({ language })
        setLocaleLanguage(language)
    }

    if (!language) {
        return <div />
    }

    return (
        <div className="wcg-flex wcg-w-4/5 wcg-flex-col wcg-items-center">
            <NavBar
                language={language}
                onLanguageChange={onLanguageChange}
            />
            <PromptEditor
                language={language}
            />
            <APIEditor
            />
        </div >
    )
}

render(<OptionsPage />, document.getElementById("options"))
