////////////////////////////////////////////////////////////////////////////////
//                                                                            //
// Copyright (C) 2024, CryptoLab Inc. All rights reserved.                    //
//                                                                            //
// This software and/or source code may be commercially used and/or           //
// disseminated only with the written permission of CryptoLab Inc,            //
// or in accordance with the terms and conditions stipulated in the           //
// agreement/contract under which the software and/or source code has been    //
// supplied by CryptoLab Inc. Any unauthorized commercial use and/or          //
// dissemination of this file is strictly prohibited and will constitute      //
// an infringement of copyright.                                              //
//                                                                            //
////////////////////////////////////////////////////////////////////////////////

#pragma once

#include "EVI/Basic.cuh"
#include "EVI/CKKSTypes.hpp"
#include "EVI/Const.hpp"
#include "EVI/Context.hpp"
#include "EVI/NTT.hpp"
#include "EVI/Type.hpp"
#include "utils/crypto/TEEWrapper.hpp"

#include "utils/Enums.hpp"
#include "utils/Exceptions.hpp"
#include "utils/SealInfo.hpp"

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

namespace evi {

namespace fs = std::filesystem;

struct SecretKeyData {
    SecretKeyData(const evi::Context &context);
    SecretKeyData(const std::string &path);

    void loadSecKey(const std::string &dir_path);
    void saveSecKey(const std::string &dir_path) const;

    void loadSealedSecKey(const std::string &dir_path);
    void saveSealedSecKey(const std::string &dir_path);

    void serialize(std::ostream &os) const;
    void deserialize(std::istream &is);

    evi::ParameterPreset preset_;

    s_poly sec_coeff_;
    poly sec_key_q_;
    poly sec_key_p_;

    bool sec_loaded_;

    std::optional<SealInfo> sInfo_;
    std::optional<TEEWrapper> teew_;
};

struct KeyPackData {
public:
    KeyPackData() = delete;
    KeyPackData(const evi::Context &context);
    KeyPackData(const evi::Context &context, std::istream &in);
    KeyPackData(const evi::Context &context, std::string &dir_path);
    ~KeyPackData() = default;

    void serialize(std::ostream &os) const;
    void deserialize(std::istream &is);

    void saveEncKeyFile(const std::string &path) const;
    void getEncKeyBuffer(std::ostream &os) const;

    void saveEvalKeyFile(const std::string &path) const;
    void getEvalKeyBuffer(std::ostream &os) const;

    void saveModPackKeyFile(const std::string &path) const;
    void getModPackKeyBuffer(std::ostream &os) const;

    void saveRelinKeyFile(const std::string &path) const;
    void getRelinKeyBuffer(std::ostream &os) const;

    void loadEncKeyFile(const std::string &path);
    void loadEncKeyBuffer(std::istream &is);

    void loadEvalKeyFile(const std::string &path);
    void loadEvalKeyBuffer(std::istream &is);

    void loadRelinKeyFile(const std::string &path);
    void loadRelinKeyBuffer(std::istream &is);

    void loadModPackKeyFile(const std::string &path);
    void loadModPackKeyBuffer(std::istream &is);

    void save(const std::string &path);

    FixedKeyType encKey;
    FixedKeyType relinKey;

    VariadicKeyType modPackKey;
    VariadicKeyType sharedAModPackKey;
    VariadicKeyType CCSharedAModPackKey;
    VariadicKeyType switchKey;
    VariadicKeyType sharedAKey;
    VariadicKeyType reverseSwitchKey;
    std::vector<VariadicKeyType> additiveSharedAKey;

    int num_shared_secret;

    bool shared_a_key_loaded_;
    bool shared_a_mod_pack_loaded_;
    bool cc_shared_a_mod_pack_loaded_;
    bool enc_loaded_;
    bool eval_loaded_;

    const evi::Context context_;
};

using KeyPack = std::shared_ptr<KeyPackData>;
using SecretKey = std::shared_ptr<SecretKeyData>;

KeyPack makeKeyPack(const evi::Context &context);
KeyPack makeKeyPack(const evi::Context &context, std::istream &in);
KeyPack makeKeyPack(const evi::Context &context, std::string &dir_path);

SecretKey makeSecKey(const evi::Context &context);
SecretKey makeSecKey(const std::string &context);

using MultiSecretKey = std::vector<std::shared_ptr<SecretKeyData>>;

} // namespace evi
