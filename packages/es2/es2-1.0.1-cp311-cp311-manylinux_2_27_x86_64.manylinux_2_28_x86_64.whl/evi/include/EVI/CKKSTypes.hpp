#pragma once

#include <memory>
#include <stdint.h>

#include <array>
#include <cstddef>
#include <functional>
#include <optional>
#include <vector>

#include "EVI/Const.hpp"
#include "EVI/Type.hpp"
#include "utils/Enums.hpp"
#include "utils/Exceptions.hpp"
#include "utils/span.hpp"

namespace evi {

#define LEVEL1 1
using Message = std::vector<float>;
using Coefficients = int *;

#define alignment_byte 256
template <typename T, std::size_t N>
struct alignas(alignment_byte) AlignedArray : public std::array<T, N> {};

using s_poly = AlignedArray<i64, DEGREE>;
using poly = AlignedArray<u64, DEGREE>;
using polyvec = std::vector<u64, AlignedAllocator<u64, alignment_byte>>;
using polyvec128 = std::vector<u128, AlignedAllocator<u128, alignment_byte>>;
using polydata = u64 *;

bool isValid(const u64 dim, const u64 degree, const u64 n);

struct IQuery {
public:
    u64 dim;
    u64 show_dim;
    u64 degree;
    u64 n;
    EncodeType encodeType;

    virtual void serializeTo(std::vector<u8> &buf) const = 0;
    virtual void deserializeFrom(const std::vector<u8> &buf) = 0;
    virtual void serializeTo(std::ostream &stream) const = 0;
    virtual void deserializeFrom(std::istream &stream) = 0;

    virtual poly &getPoly(const int i, const int level, std::optional<const int> index = std::nullopt) = 0;
    virtual const poly &getPoly(const int pos, const int level,
                                std::optional<const int> index = std::nullopt) const = 0;
    virtual polydata getPolyData(const int i, const int level, std::optional<const int> index = std::nullopt) = 0;
    virtual polydata getPolyData(const int pos, const int level,
                                 std::optional<const int> index = std::nullopt) const = 0;

    virtual polyvec128 &getPoly() = 0;
    virtual u128 *getPolyData() = 0;

    virtual DataType &getDataType() = 0;
    virtual int &getLevel() = 0;
};

template <DataType T>
struct SingleBlock : IQuery {
public:
    SingleBlock(const int level);
    SingleBlock(const poly &a_q);
    SingleBlock(const poly &a_q, const poly &b_q);
    SingleBlock(const poly &a_q, const poly &a_p, const poly &b_q, const poly &b_p);

    SingleBlock(std::istream &stream);
    SingleBlock(std::vector<u8> &buf);

    poly &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) override;
    const poly &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) const override;
    polydata getPolyData(const int pos, const int leve, std::optional<const int> index = std::nullopt) override;
    polydata getPolyData(const int pos, const int level, std::optional<const int> index = std::nullopt) const override;

    void serializeTo(std::vector<u8> &buf) const override;
    void deserializeFrom(const std::vector<u8> &buf) override;
    void serializeTo(std::ostream &stream) const override;
    void deserializeFrom(std::istream &stream) override;

    DataType &getDataType() override {
        return dtype;
    }
    int &getLevel() override {
        return level_;
    }

    // For SerializedQuery instantiaton
    [[noreturn]] polyvec128 &getPoly() override {
        throw InvalidAccessError("Not compatible type to access to 128-bit array");
    }
    [[noreturn]] u128 *getPolyData() override {
        throw InvalidAccessError("Not compatible type to access to 128-bit array");
    }

private:
    DataType dtype;
    int level_;
    poly b_q_;
    poly b_p_;
    poly a_q_;
    poly a_p_;
};

template <DataType T>
struct SerializedSingleQuery : IQuery {
    SerializedSingleQuery(polyvec128 &ptxt);

    [[noreturn]] poly &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }
    [[noreturn]] const poly &getPoly(const int pos, const int level,
                                     std::optional<const int> index = std::nullopt) const override {

        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }
    [[noreturn]] polydata getPolyData(const int pos, const int leve,
                                      std::optional<const int> index = std::nullopt) override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }
    [[noreturn]] polydata getPolyData(const int pos, const int level,
                                      std::optional<const int> index = std::nullopt) const override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }

    polyvec128 &getPoly() override;
    u128 *getPolyData() override;

    // TODO!!!!!!
    void serializeTo(std::vector<u8> &buf) const override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }
    void deserializeFrom(const std::vector<u8> &buf) override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }
    void serializeTo(std::ostream &stream) const override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }
    void deserializeFrom(std::istream &stream) override {
        throw InvalidAccessError("Not compatible type to access to 64-bit array");
    }

    DataType &getDataType() override {
        return dtype;
    }
    int &getLevel() override {
        return level_;
    }

private:
    DataType dtype;
    int level_;

    polyvec128 ptxt;
};

// using Query = std::shared_ptr<IQuery>;
using SingleQuery = std::shared_ptr<IQuery>;
using Query = std::vector<SingleQuery>;

struct IData {
public:
    u64 dim;
    u64 degree;
    u64 n;

    virtual polyvec &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) = 0;
    virtual const polyvec &getPoly(const int pos, const int level,
                                   std::optional<const int> index = std::nullopt) const = 0;
    virtual polydata getPolyData(const int pos, const int level, std::optional<const int> index = std::nullopt) = 0;
    virtual polydata getPolyData(const int pos, const int level,
                                 std::optional<const int> index = std::nullopt) const = 0;

    virtual void serializeTo(std::vector<u8> &buf) const = 0;
    virtual void deserializeFrom(const std::vector<u8> &buf) = 0;
    virtual void serializeTo(std::ostream &stream) const = 0;
    virtual void deserializeFrom(std::istream &stream) = 0;

    virtual void setSize(const int size, std::optional<int> = std::nullopt) = 0;

    virtual DataType &getDataType() = 0;
    virtual int &getLevel() = 0;
};

template <DataType T>
struct Matrix : public IData {
public:
    Matrix(const int level);
    Matrix(polyvec q);
    Matrix(polyvec a_q, polyvec b_q);
    Matrix(polyvec a_q, polyvec a_p, polyvec b_q, polyvec b_p);

    polyvec &getPoly(const int pos, const int level, std::optional<const int> index = std::nullopt) override;
    polydata getPolyData(const int pos, const int level, std::optional<const int> index = std::nullopt) override;
    const polyvec &getPoly(const int pos, const int level,
                           std::optional<const int> index = std::nullopt) const override;
    polydata getPolyData(const int pos, const int level, std::optional<const int> index = std::nullopt) const override;

    void serializeTo(std::vector<u8> &buf) const override;
    void deserializeFrom(const std::vector<u8> &buf) override;
    void serializeTo(std::ostream &stream) const override;
    void deserializeFrom(std::istream &stream) override;

    void setSize(const int size, std::optional<int> = std::nullopt) override;
    DataType &getDataType() override {
        return dtype;
    }
    int &getLevel() override {
        return level_;
    }

private:
    DataType dtype;
    int level_;
    polyvec a_q_;
    polyvec a_p_;
    polyvec b_q_;
    polyvec b_p_;
};

// using DataState = std::vector<std::shared_ptr<IData>>;
using DataState = std::shared_ptr<IData>;
using Blob = std::vector<DataState>;
using SearchResult = std::shared_ptr<IData>;

struct VariadicKeyType : std::shared_ptr<Matrix<DataType::CIPHER>> {
    VariadicKeyType() : std::shared_ptr<Matrix<DataType::CIPHER>>(std::make_shared<Matrix<DataType::CIPHER>>(LEVEL1)) {}
    VariadicKeyType(const VariadicKeyType &to_copy) : std::shared_ptr<Matrix<DataType::CIPHER>>(to_copy) {}
};

struct FixedKeyType : std::shared_ptr<SingleBlock<DataType::CIPHER>> {
    FixedKeyType()
        : std::shared_ptr<SingleBlock<DataType::CIPHER>>(std::make_shared<SingleBlock<DataType::CIPHER>>(LEVEL1)) {}
    FixedKeyType(const FixedKeyType &to_copy) : std::shared_ptr<SingleBlock<DataType::CIPHER>>(to_copy) {}
};

template <DataType T>
struct PolyData {
    void setSize(const int size);
    int getSize() const;
    polydata &getPolyData(const int pos, const int level, std::optional<int> idx = std::nullopt);

private:
    std::vector<polydata> a_q;
    std::vector<polydata> a_p;
    std::vector<polydata> b_q;
    std::vector<polydata> b_p;
};

template <DataType T>
using DeviceData = std::shared_ptr<PolyData<T>>;

} // namespace evi
